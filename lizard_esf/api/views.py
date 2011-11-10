# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
"""
API views not coupled to models.
"""

from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict

from djangorestframework.response import Response
from djangorestframework import status
from djangorestframework.views import View

from lizard_esf.models import Configuration
from lizard_esf.models import AreaConfiguration
from lizard_esf.models import tree

from lizard_esf.forms import ConfigurationForm

from lizard_area.models import Area

import json


class TreeView(View):
    """
    Specialized view for reading and updating objects in a treeform.
    """
    def get(self, request):
        return ['test']


class RootView(View):
    """
    Startpoint.
    """
    def get(self, request):
        return [{
            'configurations': reverse(
                'lizard_esf_api_configuration_root'),
        }, {
#           'area configurations': reverse(
#               'lizard_esf_api_area_configuration_root'),
#       }, {
            'configuration types': reverse(
                'lizard_esf_api_configuration_type_root'),
        }, {
            'value types': reverse(
                'lizard_esf_api_value_type_root'),
        }, {
            'tree': reverse(
                'lizard_esf_api_configuration_tree'),
        }]


class ConfigurationListView(View):
    def get(self, request):
        configs = Configuration.objects.all()
        return [(c.name, c.get_absolute_url) for c in configs]

    pass


class ConfigurationCreateView(View):
    """
    Custom view for the creation of configurations.
    """
    form = ConfigurationForm

    def get(self, request):
        return Response(status.HTTP_200_OK)

    def put(self, request):
        parent = self.CONTENT['parent']
        del self.CONTENT['parent']

        if parent:
            # Create a new child under the parent node
            parent.add_child(**self.CONTENT)
            return Response(status.HTTP_200_OK)

        # Add it as a root node
        Configuration.add_root(**self.CONTENT)
        return Response(status.HTTP_200_OK)


class ConfigurationDetailView(View):
    """
    Configuration details
    """
    def get(self, request, pk):
        cnf = Configuration.objects.get(pk=pk)
        # Beware, model_to_dict does not include
        # fields that have editable=False
        return model_to_dict(cnf, exclude=['path', 'numchild', 'depth'])


class ConfigurationTreeView(View):
    """
    Treeview, basically a dump_bulk() from treebeard
    """
    def get(self, request):

        area = request.GET.get('object_id', None)
        area = Area.objects.get(ident=area)

        area_config = AreaConfiguration.objects.filter(area=area)

        tree_data = tree(area_config)

        return tree_data

    def post(self, request, pk=None):

        data = json.loads(self.CONTENT.get('data', []))
        if type(data) == dict:
            data = [data]
        for record in data:
            area_config = AreaConfiguration.objects.get(id=int(record['id']))
            del record['id']
            for (key, value) in record.items():
                setattr(area_config, key, value)
            area_config.save()

        return {'success': True}
