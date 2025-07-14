import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import UserMemory, TeamMemory, OrganizationMemory

logger = logging.getLogger(__name__)

def get_memory_type(instance):
    """Get the memory type string based on the instance type."""
    if isinstance(instance, UserMemory):
        return "user"
    elif isinstance(instance, TeamMemory):
        return "team"
    elif isinstance(instance, OrganizationMemory):
        return "organization"
    return None


@receiver(post_save, sender=UserMemory)
@receiver(post_save, sender=TeamMemory)
@receiver(post_save, sender=OrganizationMemory)
def handle_memory_save(sender, instance, created, **kwargs):
    """
    Handle memory creation and updates.
    Triggers appropriate mem0 tasks when memories are saved.
    """
    memory_type = get_memory_type(instance)
    if not memory_type:
        logger.error(f"Unknown memory type for instance {instance}")
        return
    
    # Check if this is a programmatic status update (avoid infinite loops)
    if hasattr(instance, '_skip_signals'):
        return
    
    try:
        # Import tasks here to avoid circular imports
        from .tasks import mem0_add_task, mem0_update_task
        
        if created:
            # New memory - create in mem0
            logger.info(f"Creating new {memory_type} memory {instance.pk} in mem0")
            mem0_add_task.delay(memory_type, instance.pk, instance.content)
        else:
            # Updated memory - only sync if content changed and we have a mem0_id
            if instance.mem0_memory_id:
                # Check if content was actually changed
                # We need to compare with the database version
                try:
                    db_instance = sender.objects.get(pk=instance.pk)
                    if hasattr(instance, '_original_content') and instance._original_content != instance.content:
                        logger.info(f"Updating {memory_type} memory {instance.pk} in mem0")
                        mem0_update_task.delay(memory_type, instance.pk, instance.mem0_memory_id, instance.content)
                except sender.DoesNotExist:
                    pass
    except Exception as e:
        logger.error(f"Failed to queue Celery task for {memory_type} memory {instance.pk}: {str(e)}")
        # If we can't queue the task, mark the memory as failed
        try:
            instance._skip_signals = True
            instance.status = 'failed'
            instance.error_message = f"Failed to queue Celery task: {str(e)}"
            instance.save(update_fields=['status', 'error_message'])
        except:
            pass


@receiver(post_delete, sender=UserMemory)
@receiver(post_delete, sender=TeamMemory)
@receiver(post_delete, sender=OrganizationMemory)
def handle_memory_delete(sender, instance, **kwargs):
    """
    Handle memory deletion.
    Triggers mem0 delete task when memories are deleted.
    """
    memory_type = get_memory_type(instance)
    if not memory_type:
        logger.error(f"Unknown memory type for instance {instance}")
        return
    
    if instance.mem0_memory_id:
        try:
            # Import tasks here to avoid circular imports
            from .tasks import mem0_delete_task
            
            logger.info(f"Deleting {memory_type} memory {instance.pk} from mem0")
            mem0_delete_task.delay(memory_type, instance.pk, instance.mem0_memory_id)
        except Exception as e:
            logger.error(f"Failed to queue Celery delete task for {memory_type} memory {instance.pk}: {str(e)}")
            # For deletions, we can't update the instance since it's being deleted
            # Just log the error
