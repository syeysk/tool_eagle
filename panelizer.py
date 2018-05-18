'''
Panelizer for EagleCad printed circuit boards

'''

import xml.etree.ElementTree as ET
import re

class _Panelizer():
    def __init__(self):
        pass

    def _move(self, el, into, level=0):
        #print('  '*level, el.tag)

        for child in el:
            #print(len(child), dir(child))
            #exit()
        
            if child.tag == 'libraries': # библиотеки

                continue

            elif child.tag == 'wire' and child.get('layer') == '20': # границы печатной платы
            
                continue # продолжаем на этом же уровне

            else:

                self.move_obj(child, into)

            if len(el) > 0: self._move(child, into, level+1)

    def is_lib_exists(self, root, libname, packname=None):
        xpath = "./drawing/board/libraries/library[@name='"+libname+"']"
        if packname is not None: xpath += "/packages/package[@name='"+packname+"']"
        return root.findall(xpath)

    def move_obj(self, obj, into):
        if 'x' in obj.keys(): obj.set('x', str(float(obj.get('x')) + into['x']))
        if 'y' in obj.keys(): obj.set('y', str(float(obj.get('y')) + into['y']))

        #if 'dx' in obj.keys(): obj.set('dx', str(float(obj.get('dx')) + into['x']))
        #if 'dy' in obj.keys(): obj.set('dy', str(float(obj.get('dy')) + into['y']))

        if 'x1' in obj.keys(): obj.set('x1', str(float(obj.get('x1')) + into['x']))
        if 'x2' in obj.keys(): obj.set('x2', str(float(obj.get('x2')) + into['x']))
        if 'y1' in obj.keys(): obj.set('y1', str(float(obj.get('y1')) + into['y']))
        if 'y2' in obj.keys(): obj.set('y2', str(float(obj.get('y2')) + into['y']))

    def _join(self, board, board_to, into, postfix):

        # plain
        
        plain_to = board_to.findall('./drawing/board/plain')[0]

        for obj in board.findall('./drawing/board/plain/*'):
            if obj.tag == 'wire' and obj.get('layer') == '20': continue
            self.move_obj(obj, into)
            plain_to.append(obj)
        # signals

        signals_to = board_to.findall('./drawing/board/signals')[0]
        
        for signal in board.findall('./drawing/board/signals/*'):
            
            signal.set('name', signal.get('name')+postfix)
            for child in signal:
                self.move_obj(child, into)
                if child.tag == 'contactref': child.set('element', child.get('element')+postfix)
                for vertex in child: # for polygon
                    self.move_obj(vertex, into)                
            signals_to.append(signal)
           
        # elements

        elements_to = board_to.findall('./drawing/board/elements')[0]
        
        for element in board.findall('./drawing/board/elements/*'):
            element.set('name', element.get('name')+postfix)
            self.move_obj(element, into)
            for attribute in element:
                self.move_obj(attribute, into)
            elements_to.append(element)
            
        # libraries

        libraries_to = board_to.findall('./drawing/board/libraries')[0]
        
        for library in board.findall('./drawing/board/libraries/*'):
            library_to = self.is_lib_exists(board_to, library.get('name'))
            if library_to:
                packages_to = library_to[0].findall("./packages")[0]
                for package in library.findall('./packages/*'):
                    if self.is_lib_exists(board_to, library.get('name'), package.get('name')): continue
                    packages_to.append(package)
                continue
            libraries_to.append(library)

    def _set_board_bound(self, root, coords):
        
        points = [{'x1':coords['x1'], 'y1':coords['y1'], 'x2':coords['x1'], 'y2':coords['y2']},
                  {'x1':coords['x1'], 'y1':coords['y2'], 'x2':coords['x2'], 'y2':coords['y2']},
                  {'x1':coords['x2'], 'y1':coords['y2'], 'x2':coords['x2'], 'y2':coords['y1']},
                  {'x1':coords['x1'], 'y1':coords['y1'], 'x2':coords['x2'], 'y2':coords['y1']}]

        for i, wire in enumerate(root.findall("./drawing/board/plain/wire[@layer='20']")):
            coords = points[i]
            wire.set('x1', str(coords['x1']))
            wire.set('y1', str(coords['y1']))
            wire.set('x2', str(coords['x2']))
            wire.set('y2', str(coords['y2']))

    '''def _get_fact_board_bound(self, root):
        x = []
        y = []
        for obj in root:
            if obj.tag == 'libraries':continue
            for name in ['x1', 'x2']: x.append(float(obj.get(name)))
            for name in ['y1', 'y2']: y.append(float(obj.get(name)))
        return { 'x1': min(x), 'y1': min(y), 'x2': max(x), 'y2': max(y) }
    '''

    def _get_board_bound(self, root):
        x = []
        y = []
        for wire in root.findall("./drawing/board/plain/wire[@layer='20']"):
            for name in ['x1', 'x2']: x.append(float(wire.get(name)))
            for name in ['y1', 'y2']: y.append(float(wire.get(name)))
        return { 'x1': min(x), 'y1': min(y), 'x2': max(x), 'y2': max(y) }
         
    '''def _get_max_names(self, root):
        elements = [];'''
        
    def _rename_all(self, root):

        name_map = {}
        name_max = {}
        
        # rename the elements

        for element in root.findall("./drawing/board/elements/*"):
            name = element.get('name')
            prefix, index = re.sub(r"^([a-zA-Z_]+)([0-9]+)", r"\1 \2", name).split()

            if prefix not in name_max.keys(): name_max[prefix] = 1
            new_name = prefix + str(name_max[prefix])
            element.set('name', new_name)
            name_map[name] = new_name
            name_max[prefix] += 1
            #print(name, new_name)
                
                
        # rename the references to the elements
       
        for ref in root.findall("./drawing/board/signals/signal/contactref"):
            ref.set('element', name_map[ref.get('element')])

class Panelizer(_Panelizer):

    def __init__(self, docs):
        
        _Panelizer.__init__(self)
        
        self.docs = {}
        
        for fkey, fname in docs.items():
            tree = ET.parse(fname)
            root = tree.getroot()
            self.docs[fkey] = {'fname':fname, 'tree': tree, 'root': root}
           
    def get_max_names(self, fkey):
        self._get_max_names(self.docs[fkey]['root'])

    def set_board_bound(self, fkey, coords):
        return self._set_board_bound(self.docs[fkey]['root'], coords)

    def get_board_bound(self, fkey):
        return self._get_board_bound(self.docs[fkey]['root'])

    def get_fact_board_bound(self, fkey):
        return self._get_fact_board_bound(self.docs[fkey]['root'])

    def move(self, fkey, into):
        self._move(self.docs[fkey]['root'], into)

    def join(self, fkey, fkey_to, into):
        self._join(self.docs[fkey]['root'], self.docs[fkey_to]['root'], into, fkey)

    def write(self, fkey, fname_out=None):
        fname_out = self.docs[fkey]['fname'] if fname_out is None else fname_out
        self.docs[fkey]['tree'].write(fname_out)

    def rename_all(self, fkey):
        self._rename_all(self.docs[fkey]['root'])

pan = Panelizer({'tr': '../../../eagle/Termo-Relay/Termo-Relay.brd',
                 'wfr-bt139':'../../../eagle/WIFI-Relay-bt139/main.brd',
                 'wfr':'../../../eagle/WIFI-Relay_v0.2/WIFI-Relay_v0.2.brd'})

if __name__ == '__main__':

    for fkey in pan.docs:
        c = pan.get_board_bound(fkey)
        print(fkey+':', str(c['x1'])+' '+str(c['y1']), ';', str(c['x2'])+' '+str(c['y2']))

    tr_c = pan.get_board_bound('tr')
    wfr_bt_c = pan.get_board_bound('wfr-bt139')

    #pan.move('tr', {'x': 10, 'y': 50})
    pan.join('wfr', 'tr', {'x':tr_c['x2']+2, 'y':tr_c['y1']})
    pan.join('tr', 'wfr-bt139', {'x':wfr_bt_c['x1'], 'y':wfr_bt_c['y2']+1})

    #wfr_bt_c = pan.get_fact_board_bound('wfr-bt139')
    pan.set_board_bound('wfr-bt139', {'x1':0, 'y1':0, 'x2':100, 'y2':100})#wfr_bt_c)

    pan.rename_all('wfr-bt139')

    pan.write('wfr-bt139', '../../../eagle/panelizing/main.brd')

''' example of *.brd

 eagle
   drawing
     settings
       setting
       setting
     grid
     layers
       layer
       ***
       layer
     board
       plain
         wire (не медь)
         ***
         text
       libraries
         library
         ***
         library
       attributes
       variantdefs
       classes
         class
       designrules
         description
         description
         param
         ***
         param
       autorouter
         pass
           param
         ***
         pass
           param
       elements
         element
         ***
         element
           attribute
       signals
         signal
           wire
           contactref
           via
           ***
           wire
           contactref
           via
   compatibility
     note
     note
     note
     note
'''