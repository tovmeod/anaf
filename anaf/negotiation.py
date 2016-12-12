from rest_framework.negotiation import DefaultContentNegotiation


class ContentNegotiation(DefaultContentNegotiation):
    """This Class also uses the request content type to determine the response content type"""
    def get_accept_list(self, request):
        """Inserts request content type before */*, or as last"""
        accepts = super(ContentNegotiation, self).get_accept_list(request)
        try:
            accepts.insert(accepts.index('*/*'), request.content_type)
        except ValueError:  # '*/*' is not in list
            accepts.append(request.content_type)
        return accepts
