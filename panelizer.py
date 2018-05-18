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

                if 'x' in child.keys(): child.set('x', str(float(child.get('x')) + into['x']))
                if 'y' in child.keys(): child.set('y', str(float(child.get('y')) + into['y']))

                #if 'dx' in child.keys(): child.set('dx', str(float(child.get('dx')) + into['x']))
                #if 'dy' in child.keys(): child.set('dy', str(float(child.get('dy')) + into['y']))

                if 'x1' in child.keys(): child.set('x1', str(float(child.get('x1')) + into['x']))
                if 'x2' in child.keys(): child.set('x2', str(float(child.get('x2')) + into['x']))
                if 'y1' in child.keys(): child.set('y1', str(float(child.get('y1')) + into['y']))
                if 'y2' in child.keys(): child.set('y2', str(float(child.get('y2')) + into['y']))

            if len(el) > 0: self._move(child, into, level+1)

    def is_lib_exists(self, root, libname, packname=None):
        xpath = "./drawing/board/libraries/library[@name='"+libname+"']"
        if packname is not None: xpath += "/packages/package[@name='"+packname+"']"
        return root.findall(xpath)

    def _join(self, board, board_to, into):
        
        # signals

        signals_to = board_to.findall('./drawing/board/signals')[0]
        
        for signal in board.findall('./drawing/board/signals/*'):
            
            signal.set('name', signal.get('name')+'_1')
            for child in signal:
                if child.tag == 'contactref': child.set('element', child.get('element')+'_1')
            signals_to.append(signal)
           
        # elements

        elements_to = board_to.findall('./drawing/board/elements')[0]
        
        for element in board.findall('./drawing/board/elements/*'):
            element.set('name', element.get('name')+'_1')
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

    def get_board_bound(self, fkey):
        return self._get_board_bound(self.docs[fkey]['root'])

    def move(self, fkey, into):
        self._move(self.docs[fkey]['root'], into)

    def join(self, fkey, fkey_to, into):
        self._join(self.docs[fkey]['root'], self.docs[fkey_to]['root'], into)

    def write(self, fkey, fname_out=None):
        fname_out = self.docs[fkey]['fname'] if fname_out is None else fname_out
        self.docs[fkey]['tree'].write(fname_out)

pan = Panelizer({'tr': '../Termo-Relay/Termo-Relay.brd',
                 'wfr-bt139':'../WIFI-Relay-bt139/main.brd',
                 'wfr':'../WIFI-Relay_v0.2/WIFI-Relay_v0.2.brd'})

for fkey in pan.docs:
    c = pan.get_board_bound(fkey)
    print(fkey+':', str(c['x1'])+' '+str(c['y1']), ';', str(c['x2'])+' '+str(c['y2']))

pan.move('tr', {'x': 10, 'y': 50})
pan.join('wfr', 'tr', {'x':0, 'y':0})

pan.write('tr', '../Termo-Relay2.brd')


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