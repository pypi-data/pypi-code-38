# Enise widgets for guizero
from enisegui.table         import Table
from enisegui.autotextboxkv import AutoTextBoxKV
from enisegui.datetextbox   import DateTextBox
from enisegui.combokv       import ComboKV
from enisegui.listboxkv     import ListBoxKV

# test code
def Demo():
    from guizero import App,Box,Text,ButtonGroup,PushButton
    import pkg_resources 
    
    curdir = pkg_resources.resource_filename('enisegui','.')

    sep_pad = 2
    app   = App(width=650, height=560) 
    mainbox = Box(app, width='fill')
    Box(mainbox, width='fill', height=sep_pad)
    
    # champ autocomplété   
    def choicelist(pattern):
        return [w for w in autolist if pattern in w]
        
    def choicelistKV(pattern):
        return [autolistKV[i] for i in range(len(autolistKV))
                        if pattern in autolistKV[i][0]]
    def auto_get(key):
        if key:
            autoval.value = key
        else:
            autoval.value = 'None'
        
    with open(curdir+'/autolist.txt') as file:
        autolist = file.read()
    autolist   = autolist.split('\n')
    autolistKV = [(autolist[i],'key-'+str(i)) for i in range(len(autolist))]

    autobox = Box(app, width='fill')
    Box(autobox, height='fill', width=4, align='left')
    autotext = Text(autobox, text='AutoTextBoxKV', width=18, align='left')
    autotext.tk.config(font='Helvetica 12 bold')
    autotext.tk.config(anchor='w')
    auto   = AutoTextBoxKV(autobox, length=20, max=6, text='Holmes Scott',
                            change=choicelistKV, command=auto_get, align='left')
    Box(autobox, width=4, height='fill', align='left')
    Text(autobox, text=' Key : ', align='left')
    autoval = Text(autobox, text='--', bg='green', color='white', align='left')
    auto.focus()
    
    # séparateur
    mainbox = Box(app, width='fill')
    Box(mainbox, width='fill', height=sep_pad)
    box = Box(mainbox, width='fill')
    Box(box, height='fill', width=4, align='left')
    sep = Box(box, width='fill', height=2, align='left')
    sep.set_border(1, 'grey50')
    Box(box, height=10, width=4, align='left')
    Box(mainbox, width='fill', height=sep_pad)
    
    # ComboKV
    def combo_get(key):
        combo_label.value  = key
        combo2.value = key
        
    def combo_set(value):
        combo.selectkey(value)
        
    box    = Box(app,width='fill')
    Box(box, height='fill', width=4, align='left')
    autotext = Text(box, text='ComboKV', width=18, align='left')
    autotext.tk.config(font='Helvetica 12 bold')
    autotext.tk.config(anchor='w')
    combo  = ComboKV(box, align='left', width=5,
                        options=[('Green', 12),('Yellow', 25),('Blue', 5)], 
                        command=combo_get)
    Text(box, align='left', text=' Key get ')
    combo_label  = Text(box, align='left', text='--', width=2, bg='green', color='white')
    Text(box, align='left', text=' Key set ')    
    combo2 = ComboKV(box, align='left', width=2, options=[12,25,5], command=combo_set)

    # séparateur
    mainbox = Box(app, width='fill')
    Box(mainbox, width='fill', height=sep_pad)
    box = Box(mainbox, width='fill')
    Box(box, height='fill', width=4, align='left')
    sep = Box(box, width='fill', height=2, align='left')
    sep.set_border(1, 'grey50')
    Box(box, height=10, width=4, align='left')
    Box(mainbox, width='fill', height=sep_pad)
    
    # ListBoxKV
    def listbox_get(key):
        listbox_label.value  = key
        listbox2.value = key
        
    def listbox_set(value):
        listbox.selectkey(value)
        
    box    = Box(app,width='fill')
    Box(box, height='fill', width=4, align='left')
    autotext = Text(box, text='ListBoxKV', width=18, align='left')
    autotext.tk.config(font='Helvetica 12 bold')
    autotext.tk.config(anchor='w')
    listbox  = ListBoxKV(box, align='left', width=100, height=60,
                        items=[('Green', 12),('Yellow', 25),('Blue', 5)], 
                        command=listbox_get)
    Text(box, align='left', text=' Key get ')
    listbox_label  = Text(box, align='left', text='--', width=2, bg='green', color='white')
    Text(box, align='left', text=' Key set ')    
    listbox2 = ListBoxKV(box, align='left', width=100, height=60,
                    items=[12, 25, 5], command=listbox_set)
    
    # séparateur
    mainbox = Box(app, width='fill')
    Box(mainbox, width='fill', height=sep_pad)
    box = Box(mainbox, width='fill')
    Box(box, height='fill', width=4, align='left')
    sep = Box(box, width='fill', height=2, align='left')
    sep.set_border(1, 'grey50')
    Box(box, height=10, width=4, align='left')
    Box(mainbox, width='fill', height=sep_pad)
    
    # date picker
    datebox = Box(app, width='fill')
    Box(datebox, height='fill', width=4, align='left')
    datetext = Text(datebox, text='DateTextBox', width=12, align='left')
    datetext2 = Text(datebox, text='(unfilled)', width=10, align='left')
    datetext.tk.config(font='Helvetica 12 bold')
    datetext.tk.config(anchor='w')
    datetext2.tk.config(anchor='w')
    date1 = DateTextBox(datebox, length=20, align='left')   # empty one    
    def date1_set():
        date1.value=d1.value
    PushButton(datebox, align='left', text='Set', command=date1_set)
    d1 = Text(datebox, text='1998-01-05', bg='blue', color='white', align='left')
    
    datebox = Box(app, width='fill')
    Box(datebox, height='fill', width=4, align='left')
    datetext = Text(datebox, text='DateTextBox', width=12, align='left')
    datetext2 = Text(datebox, text='(prefilled)', width=10, align='left')
    datetext.tk.config(font='Helvetica 12 bold')
    datetext.tk.config(anchor='w')
    datetext2.tk.config(anchor='w')
    date2 = DateTextBox(datebox, length=20, 
                        text='2012-05-08',    # pre-filled one
                        align='left')
    def date2_get():
        d2.value=date2.value
    PushButton(datebox, align='left', text='Get', command=date2_get)
    d2 = Text(datebox, text='--', bg='green', color='white', align='left')
    
    # séparateur
    mainbox = Box(app, width='fill')
    Box(mainbox, width='fill', height=sep_pad)
    box = Box(mainbox, width='fill')
    Box(box, height='fill', width=4, align='left')
    sep = Box(box, width='fill', height=2, align='left')
    sep.set_border(1, 'grey50')
    Box(box, height=10, width=4, align='left')
    Box(mainbox, width='fill', height=sep_pad)
    
    # tables
    data1 = [                               # liste de tuples
        ('id','name','price'),
        (251,'Orange',12.5),
        (6852,'Potatoe',1220),
        (31,'Fruit',858.5)
    ]
    
    data2 = [                 # liste de dictionnaires sans rowid
        {'id':75,'name':'Kiwi','price':3.5,'family':'fruit'},
        {'id':542,'name':'Tomatoe','price':7.50,'family':'vegetable'},
        {'id':12,'name':'Fuji','price':4.0,'family':'apple'}
    ]        
    
    data3 = [                 # liste de dictionnaires avec rowid
        {'rowid':75,'name':'Kiwi','price':3.5,'family':'fruit'},
        {'rowid':542,'name':'Tomatoe','price':7.50,'family':'vegetable'},
        {'rowid':12,'name':'Fuji','price':4.0,'family':'apple'}
    ]      
    
    def to_rowid(list):
        for i in range(len(list)):
            dict = list[i]
            if 'id' in dict:
                rowid = dict['id']
                del dict['id']
                dict['rowid'] = rowid
        return list
            
    def to_id(list):
        for i in range(len(list)):
            dict = list[i]
            if 'rowid' in dict:
                id = dict['rowid']
                del dict['rowid']
                dict['id'] = id
        return list
    
    # callbacks
    def table_action(num):
        label.value = str(num)
        
    def table_fill():
        command = {"1":None,  "2":table_action}
        rowid   = {"1":False, "2":True}
        if choose_data.value=="1":
            data = data1
        elif (choose_data.value, choose_rowid.value)==("2","1"):
            data = to_id(data2)
        elif (choose_data.value, choose_rowid.value)==("2","2"):
            data = to_rowid(data2)
        table.rowid = rowid[choose_rowid.value]
        table.data  = data
        table.update_command(command[choose_command.value])
        label.value   = "--"
    # panneau de contrôle
    panneau        = Box(app, width='fill')
    topbox         = Box(panneau, width='fill')
    Box(topbox, height='fill', width=4, align='left')
    tabletext = Text(topbox, text='Table', align='left')
    tabletext.tk.config(font='Helvetica 12 bold')
    mainbox        = Box(panneau, width='fill')
    choose_data    = ButtonGroup(mainbox, 
                            options=[["tuples", "1"],["dicts", "2"]],
                            selected="1", 
                            command=table_fill, align='left')
    choose_rowid   = ButtonGroup(mainbox, 
                            options=[["no rowid", "1"],["rowid", "2"]],
                            selected="2", 
                            command=table_fill, align='left')
    choose_command = ButtonGroup(mainbox, 
                            options=[["no command", "1"],["command", "2"]],
                            selected="1", 
                            command=table_fill, align='left')
    Text(mainbox, text='Line # : ', align='left')
    label  = Text(mainbox, text='--', bg='green', color='white', align='left')
    
    # zone d'affichage pour la table
    affichage   = Box(app, width='fill')
    topbox      = Box(affichage, width='fill', height=10)
    mainbox     = Box(affichage, width='fill')
    Box(mainbox, align='left', height='fill', width=10)
    table       = Table(mainbox, data=data1, align='left', rowid=True)
    
    
    app.display() 

