import abc


class Extractor(abc.ABC):
    ins: dict
    outs: dict
    params: dict
    secrets: dict
    confs: list
    dependencies: list

    def __init__(self, notebook, cell_source):
        self.notebook = notebook
        self.cell_source = cell_source

        self.ins = self.infer_cell_inputs()
        self.outs = self.infer_cell_outputs()
        self.params = self.extract_cell_params(cell_source)
        self.secrets = self.extract_cell_secrets(cell_source)
        self.confs = self.extract_cell_conf_ref()
        self.dependencies = self.infer_cell_dependencies(self.confs)

    @abc.abstractmethod
    def infer_cell_inputs(self):
        pass

    @abc.abstractmethod
    def infer_cell_outputs(self):
        pass

    @abc.abstractmethod
    def extract_cell_params(self, source):
        pass

    @abc.abstractmethod
    def extract_cell_secrets(self, source):
        pass

    @abc.abstractmethod
    def extract_cell_conf_ref(self):
        pass

    @abc.abstractmethod
    def infer_cell_dependencies(self, confs):
        pass


class DummyExtractor(Extractor):
    def infer_cell_inputs(self):
        return {}

    def infer_cell_outputs(self):
        return {}

    def extract_cell_params(self, source):
        return {}

    def extract_cell_secrets(self, source):
        return {}

    def extract_cell_conf_ref(self):
        return []

    def infer_cell_dependencies(self, confs):
        return []
