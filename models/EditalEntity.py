class EditalEntity:
    def __init__(self, id, chaveEdital, numeroPregao, orgao, lote, lastMessageDate):
        self.id = id
        self.chaveEdital = chaveEdital
        self.numeroPregao = numeroPregao
        self.orgao = orgao
        self.lote = lote
        self.lastMessageDate = lastMessageDate

    def __str__(self):
        return f"id: {self.id}, chaveEdital: {self.chaveEdital}, numeroPregao: {self.numeroPregao}, orgao: {self.orgao}, lote: {self.lote}, lastmessage: {self.lastMessageDate}"