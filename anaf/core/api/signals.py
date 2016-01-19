def consumer_post_save(sender, instance, created, **kwargs):
    pass


def consumer_post_delete(sender, instance, **kwargs):
    instance.status = 'canceled'