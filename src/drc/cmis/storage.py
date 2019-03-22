from io import BytesIO


class BinaireInhoud:
    def __init__(self, data, filename):
        self.data = data
        self.bestandsnaam = filename

    def to_cmis(self) -> BytesIO:
        if self.data is None:
            return None

        return BytesIO(self.data)
