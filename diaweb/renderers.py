from rest_framework.renderers import TemplateHTMLRenderer

class WebUserTemplateHTMLRenderer(TemplateHTMLRenderer):

    def get_template_context(self, data, renderer_context):
        data = super().get_template_context(data, renderer_context)
        if not data:
            return {}
        else:
            return {'data': data}