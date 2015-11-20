from core.models import Service, TenantWithContainer
from django.db import transaction

HELLO_WORLD_KIND = "helloworldservice"

class HelloWorldService(Service):
    KIND = HELLO_WORLD_KIND

    class Meta:
	proxy = True
	app_label = "helloworldservice"
	verbose_name = "Hello World Service"

class HelloWorldTenant(TenantWithContainer):
    class Meta:
        proxy = True

    KIND = HELLO_WORLD_KIND
    sync_attributes = ("private_ip", "private_mac",
                       "nat_ip", "nat_mac",)

    default_attributes = {'display_message': 'Hello World!'}
    def __init__(self, *args, **kwargs):
        helloworld_services = HelloWorldService.get_service_objects().all();
    	if helloworld_services:
                self._meta.get_field("provider_service").default = helloworld_services[0].id
    	super(HelloWorldTenant, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(HelloWorldTenant, self).save(*args, **kwargs)
        model_policy_helloworld_tenant(self.pk)

    def delete(self, *args, **kwargs):
        self.cleanup_container()
        super(HelloWorldTenant, self).delete(*args, **kwargs)

    @property
    def display_message(self):
        return self.get_attribute(
		"display_message",
		self.default_attributes['display_message'])

    @display_message.setter
    def display_message(self, value):
        self.set_attribute("display_message", value)

    @property
    def addresses(self):
        if (not self.id) or (not self.instance):
            return {}

        addresses = {}
        for ns in self.instance.ports.all():
            if "nat" in ns.network.name.lower():
                addresses["nat"] = (ns.ip, ns.mac)
            elif "private" in ns.network.name.lower():
                addresses["private"] = (ns.ip, ns.mac)
        return addresses

    @property
    def nat_ip(self):
        return self.addresses.get("nat", (None, None))[0]

    @property
    def nat_mac(self):
        return self.addresses.get("nat", (None, None))[1]

    @property
    def private_ip(self):
        return self.addresses.get("private", (None, None))[0]

    @property
    def private_mac(self):
        return self.addresses.get("private", (None, None))[1]

def model_policy_helloworld_tenant(pk):
    with transaction.atomic():
        tenant = HelloWorldTenant.objects.select_for_update().filter(pk=pk)
        if not tenant:
            return
        tenant = tenant[0]
        tenant.manage_container()
