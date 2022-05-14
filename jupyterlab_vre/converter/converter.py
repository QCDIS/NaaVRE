import uuid
from colorhash import ColorHash

class ConverterReactFlowChart:

    @staticmethod
    def get_node(node_id, title, ins, outs, params, deps):

        node = {}
        position = {}
        ports = {}
        properties = {}

        node['id']                  = node_id
        node['type']                = 'input-output'
        position['x']               = 35
        position['y']               = 15
        node['position']            = position
        properties['title']         = title
        properties['vars']          = list()
        properties['params']        = list(params)
        properties['inputs']        = list(ins)
        properties['outputs']       = list(outs)
        properties['og_node_id']    = node_id
        properties['deps']          = list()
        node['properties']          = properties

        for i in ins:
            ports[i] = {}
            ports[i]['properties'] = {}
            ports[i]['id'] = i
            ports[i]['type'] = 'left'
            ports[i]['properties']['color'] = ColorHash(i).hex
            properties['vars'].append({ 
                'name'      : i,
                'direction' : 'input',
                'type'      : 'datatype',
                'color'     : ports[i]['properties']['color']
            })

        for o in outs:
            ports[o] = {}
            ports[o]['properties'] = {}
            ports[o]['id'] = o
            ports[o]['type'] = 'right'
            ports[o]['properties']['color'] = ColorHash(o).hex
            properties['vars'].append({ 
                'name'      : o,
                'direction' : 'output',
                'type'      : 'datatype',
                'color'     : ports[o]['properties']['color']
            })

        node['ports'] = ports

        for dep in deps:
            properties['deps'].append(dep['module'].split('.')[0])

        properties['deps'] = list(set(properties['deps']))

        return node


class ConverterReactFlow:

    @staticmethod
    def get_input_nodes(ins):
        nodes = []
        idx = 0

        for i in ins:
            i_node = {}
            i_node['data'] = {}
            i_node['position'] = {}
            i_node['id'] = i
            i_node['type'] = 'input'
            i_node['data']['label'] = i
            i_node['position']['x'] = 10 + idx * 200
            i_node['position']['y'] = 10
            nodes.append(i_node)
            idx += 1

        return nodes


    @staticmethod
    def get_output_nodes(outs):
        nodes = []
        idx = 0

        for o in outs:
            o_node = {}
            o_node['data'] = {}
            o_node['position'] = {}
            o_node['id'] = o
            o_node['type'] = 'output'
            o_node['data']['label'] = o
            o_node['position']['x'] = 10 + idx * 200
            o_node['position']['y'] = 200
            nodes.append(o_node)
            idx += 1

        return nodes

    
    @staticmethod
    def get_default_node(title, uuid):
        d_node = {}
        d_node['data'] = {}
        d_node['position'] = {}
        d_node['id'] = uuid
        d_node['data']['label'] = title
        d_node['position']['x'] = 100
        d_node['position']['y'] = 100

        return d_node
    

    @staticmethod
    def get_edges(d_node_id, ins, outs):
        edges = []

        for i in ins:
            i_edge = {}
            i_edge['id'] = "%s-%s" % (i, d_node_id)
            i_edge['source'] = i
            i_edge['target'] = d_node_id
            i_edge['animated'] = True
            edges.append(i_edge)

        for o in outs:
            o_edge = {}
            o_edge['id'] = "%s-%s" % (d_node_id, o)
            o_edge['source'] = d_node_id
            o_edge['target'] = o
            o_edge['animated'] = True
            edges.append(o_edge)

        return edges


class ConverterFlume:

    @staticmethod
    def get_ports(ins, outs):
        colors = [
            'yellow',
            'orange',
            'red',
            'pink',
            'purple',
            'blue',
            'green',
            'grey'
        ]

        ports = set()
        ports_types = []

        ports.update(ins)
        ports.update(outs)

        color_i = 0
        for port in ports:

            p_type = {}
            p_type['type'] = port
            p_type['name'] = port
            p_type['label'] = port
            p_type['color'] = colors[color_i],
            color_i = (color_i + 1) % len(colors)

            ports_types.append(p_type)

        return ports_types


    @staticmethod
    def get_node(source, ports, ins, outs):
        title = source.partition('\n')[0]
        short_uuid = str(uuid.uuid4())[:7]

        n_type = {}
        n_type['type'] = short_uuid
        n_type['label'] = title if title[0] == "#" else "Untitled %s" % short_uuid
        n_type['description'] = short_uuid

        ports_in = [ p for p in ports if p['name'] in ins ]
        ports_out = [ p for p in ports if p['name'] in outs ]

        n_type['inputs'] = ports_in
        n_type['outputs'] = ports_out

        return n_type



