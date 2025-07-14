import logging
from celery import shared_task
from mem0 import MemoryClient
from django.apps import apps
from django.conf import settings

logger = logging.getLogger(__name__)

# Shared Memory instance per worker process
_mem0_instance = None


def get_mem0_instance():
    """Get or create a shared MemoryClient instance for the current worker."""
    global _mem0_instance
    if _mem0_instance is None:
        if not settings.MEM0_API_KEY:
            raise ValueError(
                "MEM0_API_KEY must be set in settings to create MemoryClient instance"
            )
        _mem0_instance = MemoryClient(api_key=settings.MEM0_API_KEY)
        logger.info("Created new MemoryClient instance for worker")
    return _mem0_instance


def get_model_class(memory_type):
    """Get the model class based on memory type."""
    if memory_type == "user":
        return apps.get_model("memories", "UserMemory")
    elif memory_type == "team":
        return apps.get_model("memories", "TeamMemory")
    elif memory_type == "organization":
        return apps.get_model("memories", "OrganizationMemory")
    else:
        raise ValueError(f"Invalid memory type: {memory_type}")


@shared_task(bind=True, max_retries=3)
def mem0_add_task(self, memory_type, pk, content):
    """
    Create a new memory in mem0 and update the status.
    """
    try:
        # Get the appropriate model class
        model_class = get_model_class(memory_type)
        # Get the instance and mark as processing
        instance = model_class.objects.get(pk=pk)
        instance.mark_as_processing()

        # Create memory in mem0
        client = get_mem0_instance()

        user_id = f"{memory_type}_{pk}"
        message = [{"role": "user", "content": content}]
        result = client.add(message, user_id=user_id)

        # Extract mem0_memory_id from result
        if result and "results" in result and len(result["results"]) > 0:
            mem0_id = result["results"][0]["id"]

            # Update the instance with mem0_memory_id and mark as completed
            instance.mem0_memory_id = mem0_id
            instance.mark_as_completed()

            logger.info(
                f"Successfully created mem0 memory for {memory_type} {pk}: {mem0_id}"
            )
        else:
            raise Exception("Invalid response from mem0")

    except Exception as exc:
        logger.error(f"Error creating mem0 memory for {memory_type} {pk}: {str(exc)}")

        # Get the instance and mark as failed
        try:
            instance = model_class.objects.get(pk=pk)
            instance.mark_as_failed(str(exc))
        except:
            pass

        # Retry if we haven't exceeded max_retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=10)
        else:
            raise exc


@shared_task(bind=True, max_retries=3)
def mem0_update_task(self, memory_type, pk, mem0_id, content):
    """
    Update an existing memory in mem0 and update the status.
    """
    try:
        # Validate mem0_id
        if not mem0_id:
            self.mem0_add_task(memory_type, pk, content)
        # Get the appropriate model class
        model_class = get_model_class(memory_type)

        # Get the instance and mark as processing
        instance = model_class.objects.get(pk=pk)
        instance.mark_as_processing()

        # Update memory in mem0
        client = get_mem0_instance()
        client.update(memory_id=mem0_id, data=content)

        # Mark as completed
        instance.mark_as_completed()

        logger.info(
            f"Successfully updated mem0 memory for {memory_type} {pk}: {mem0_id}"
        )

    except Exception as exc:
        logger.error(f"Error updating mem0 memory for {memory_type} {pk}: {str(exc)}")

        # Get the instance and mark as failed
        try:
            instance = model_class.objects.get(pk=pk)
            instance.mark_as_failed(str(exc))
        except:
            pass

        # Retry if we haven't exceeded max_retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=10)
        else:
            raise exc


@shared_task(bind=True, max_retries=3)
def mem0_delete_task(self, memory_type, pk, mem0_id):
    """
    Delete a memory from mem0.
    """
    try:
        # Delete memory from mem0
        client = get_mem0_instance()
        client.delete(memory_id=mem0_id)

        logger.info(
            f"Successfully deleted mem0 memory for {memory_type} {pk}: {mem0_id}"
        )

    except Exception as exc:
        logger.error(f"Error deleting mem0 memory for {memory_type} {pk}: {str(exc)}")

        # Retry if we haven't exceeded max_retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=10)
        else:
            raise exc
