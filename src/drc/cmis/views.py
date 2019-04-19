from django.http.response import Http404, HttpResponse
from django.utils.encoding import smart_str
from django.views.generic import DetailView

from drc.datamodel.models import EnkelvoudigInformatieObject

from .client import default_client


class DownloadFileView(DetailView):
    model = EnkelvoudigInformatieObject
    slug_field = 'uuid'
    slug_url_kwarg = 'inhoud'

    def get(self, request, *args, **kwargs):
        document = self.get_object()
        filename, content = default_client.geef_inhoud(document)

        file_content = content.read()

        if file_content:
            response = HttpResponse(file_content, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename=%s.bin' % smart_str(filename)
            return response
        raise Http404
