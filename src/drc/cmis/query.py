class CMISQuery:
    """
    Small, not feature-complete utility class for building CMIS queries with
    escaping built in.

    Usage:
    >>> query = CMSQuery("SELECT * FROM cmis:document WHERE cmis:objectTypeId = '%s'")
    >>> query('zsdms:document')
    "SELECT * FROM cmis:document WHERE cmis:objectTypeId = 'zsdms:document';"
    """

    def __init__(self, query):
        self.query = query

    def __call__(self, *args):
        args = tuple((self.escape(arg) for arg in args))
        return self.query % args

    def escape(self, value):
        """
        Escapes the characters in value for the CMIS queries.

        Poor documentation references:
          * https://community.alfresco.com/docs/DOC-5898-cmis-query-language#Literals
          * http://docs.alfresco.com/community/concepts/rm-searchsyntax-literals.html
        """
        value = value.replace("'", "\\'")
        value = value.replace('"', '\\"')
        return value
