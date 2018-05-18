import xml.etree.ElementTree as ET

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
        for i, wire in enumerate(root.findall("./drawing/board/plain/wire[@layer='20']")):
            pass
            '''coords = points[i]
            wire.set('x1', coords['x1'])
            wire.set('y1', coords['y1'])
            wire.set('x2', coords['x2'])
            wire.set('y2', coords['y2'])'''

    def _get_fact_board_bound(self, root):
        x = []
        y = []
        for wire in root:
            if child.tag == 'libraries':continue
            for name in ['x1', 'x2']: x.append(float(wire.get(name)))
            for name in ['y1', 'y2']: y.append(float(wire.get(name)))
        return { 'x1': min(x), 'y1': min(y), 'x2': max(x), 'y2': max(y) }


    def _get_board_bound(self, root):
        x = []
        y = []
        for wire in root.findall("./drawing/board/plain/wire[@layer='20']"):
            for name in ['x1', 'x2']: x.append(float(wire.get(name)))
            for name in ['y1', 'y2']: y.append(float(wire.get(name)))
        return { 'x1': min(x), 'y1': min(y), 'x2': max(x), 'y2': max(y) }
         
    def _get_max_names(self, root):
        elements = [];

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

pan = Panelizer({'tr': '../Termo-Relay/Termo-Relay.brd',
                 'wfr-bt139':'../WIFI-Relay-bt139/main.brd',
                 'wfr':'../WIFI-Relay_v0.2/WIFI-Relay_v0.2.brd'})

for fkey in pan.docs:
    c = pan.get_board_bound(fkey)
    print(fkey+':', str(c['x1'])+' '+str(c['y1']), ';', str(c['x2'])+' '+str(c['y2']))

tr_c = pan.get_board_bound('tr')
wfr_bt_c = pan.get_board_bound('wfr-bt139')

#pan.move('tr', {'x': 10, 'y': 50})
pan.join('wfr', 'tr', {'x':tr_c['x2']+5, 'y':tr_c['y1']})
pan.join('tr', 'wfr-bt139', {'x':wfr_bt_c['x1'], 'y':wfr_bt_c['y2']+5})

wfr_bt_c = pan.get_fact_board_bound('wfr-bt139')
pan.set_board_bound('wfr-bt139', wfr_bt_c)

pan.write('wfr-bt139', '../Termo-Relay2.brd')


'''

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