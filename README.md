# Tools for Autodesk Eagle

## Panelizer.py

```python

import panelizer

pan = panelizer.Panelizer({
    'tr': '../../../eagle/Termo-Relay/Termo-Relay.brd',
    'wfr-bt139':'../../../eagle/WIFI-Relay-bt139/main.brd',
    'wfr':'../../../eagle/WIFI-Relay_v0.2/WIFI-Relay_v0.2.brd'
})

# getting the board bounds

tr_c = pan.get_board_bound('tr')
wfr_bt_c = pan.get_board_bound('wfr-bt139')

# move the board

#pan.move('tr', {'x': 10, 'y': 50})

# insert 'wfr' into 'tr'. The third argument - is where to move 'wfr' after inserting

pan.join('wfr', 'tr', {'x':tr_c['x2']+2, 'y':tr_c['y1']})

# insert 'tr' into 'wfr-bt139'. The third argument - is where to move 'tr' after inserting

pan.join('tr', 'wfr-bt139', {'x':wfr_bt_c['x1'], 'y':wfr_bt_c['y2']+1})

# set new board bound

pan.set_board_bound('wfr-bt139', {'x1':0, 'y1':0, 'x2':100, 'y2':100})

# rename all elements. The names will be uniq

pan.rename_all('wfr-bt139')

# save the finished board into new file

pan.write('wfr-bt139', '../../../eagle/panelizing/main.brd')

```

Thanks. No warranty - please, do backup before manupulating with your boards.