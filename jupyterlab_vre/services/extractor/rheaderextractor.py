from .headerextractor import HeaderExtractor


class RHeaderExtractor(HeaderExtractor):

    def extract_cell_conf_ref(self):
        if self.cell_header is None:
            return None
        items = self.cell_header['NaaVRE']['cell'].get('confs')
        if items is None:
            return None
        for item in items:
            for k, v in item.items():
                if 'assignation' in v:
                    assignation = v.get('assignation')
                    if '[' in assignation and ']' in assignation:
                        # Replace to R list format
                        assignation = assignation.replace('[', 'list(').replace(']', ')')
                        item[k]['assignation'] = assignation
        cell_conf = {k: v['assignation'] for it in items for k, v in it.items()}
        return cell_conf
