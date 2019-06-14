import os
qt5_cef_version = '0.0.45'
qt_class_name = 'Qt5QWindowIcon'
default_window_width = -1
default_window_height = -1
default_window_title = 'Burgeon Software'
default_nest_window_margin = 0
min_window_width = 800
min_window_height = 800 * 0.618
debug_log_dir = os.path.join('CEF-LOG', 'Debug')
language_locale = {
    '25': {
        'name': 'Chinese',
        'locale': 'zh_CN'
    },
    '59': {
        'name': 'Japanese',
        'locale': 'ja'
    }
}

burgeon_cef_sdk_js = """
(function () {
    if (window.CEF_HAS_INITIALIZED) {
        return
    }
    const encryptionKey = 'BURGEON-FRONT-END';
    const moduleName = 'windowInstance';
    const sdkModuleName = '__cef__';
    const pythonCallBack = 'python_cef';
    const cef = {
        payload: {},
        hooks: {}
    };
    const python_cef = {};
    const customEventMap = {
        windowCloseEvent: {
            name: 'windowCloseEvent',
            event: new CustomEvent('windowCloseEvent', {detail: {windowId: window.windowId}}),
            hooks: 0
        },
        windowBroadcastEvent: {
            name: 'windowBroadcastEvent',
            event: null,
            hooks: 0,
        }
    };
    python_cef.loadUrl = (url) => {
        window.location.href = url;
    };
    python_cef.console = (msg, type) => {
        switch (type) {
            case 'error':
                console.error(msg);
                break;
            case 'warn':
                console.warn(msg);
                break;
            default:
                console.log(msg);
                break;
        }
    };
    python_cef.updateCustomizePayload = (params) => {
        Object.keys(params).forEach(key => {
            cef.payload[key] = params[key]
        })
    };
    python_cef.updateCefConfig = (key, value) => {
        if (window[sdkModuleName] === undefined) {
            window[sdkModuleName] = {}
        }
        window[sdkModuleName][key] = value;
    };
    python_cef.updateThirdPartyClientInfo = (clientId, status) => {
        window[sdkModuleName].thirdPartyInfo[clientId] = status;
    };
    python_cef.dispatchCustomEvent = (eventName, eventData) => {
        switch (eventName) {
            case customEventMap.windowCloseEvent.name:
                if (!window[moduleName] || typeof window[sdkModuleName]['close'] !== 'function') {
                    return;
                }
                if (customEventMap[eventName].hooks === 0) {
                    window[sdkModuleName].close();
                } else {
                    window.dispatchEvent(customEventMap[eventName].event)
                }
                break;
            case customEventMap.windowBroadcastEvent.name:
                const event = new CustomEvent(eventName, {detail: {eventData}});
                window.dispatchEvent(event);
                break;
            default:
                break;
        }

    };
    cef.version = '0.0.46';
    cef.thirdPartyInfo = {};
    cef.VK_CODE = {
        'Backspace': 0x08,
        'Tab': 0x09,
        'Clear': 0x0C,
        'Enter': 0x0D,
        'Shift': 0x10,
        'Ctrl': 0x11,
        'Alt': 0x12,
        'Pause': 0x13,
        'CapsLock': 0x14,
        'Esc': 0x1B,
        'SpaceBar': 0x20,
        'PageUp': 0x21,
        'PageDown': 0x22,
        'End': 0x23,
        'Home': 0x24,
        'LeftArrow': 0x25,
        'UpArrow': 0x26,
        'RightArrow': 0x27,
        'DownArrow': 0x28,
        'Select': 0x29,
        'Print': 0x2A,
        'Execute': 0x2B,
        'PrintScreen': 0x2C,
        'Ins': 0x2D,
        'Del': 0x2E,
        'Help': 0x2F,
        '0': 0x30,
        '1': 0x31,
        '2': 0x32,
        '3': 0x33,
        '4': 0x34,
        '5': 0x35,
        '6': 0x36,
        '7': 0x37,
        '8': 0x38,
        '9': 0x39,
        'A': 0x41,
        'B': 0x42,
        'C': 0x43,
        'D': 0x44,
        'E': 0x45,
        'F': 0x46,
        'G': 0x47,
        'H': 0x48,
        'I': 0x49,
        'J': 0x4A,
        'K': 0x4B,
        'L': 0x4C,
        'M': 0x4D,
        'N': 0x4E,
        'O': 0x4F,
        'P': 0x50,
        'Q': 0x51,
        'R': 0x52,
        'S': 0x53,
        'T': 0x54,
        'U': 0x55,
        'V': 0x56,
        'W': 0x57,
        'X': 0x58,
        'Y': 0x59,
        'Z': 0x5A,
        'NumPad0': 0x60,
        'NumPad1': 0x61,
        'NumPad2': 0x62,
        'NumPad3': 0x63,
        'NumPad4': 0x64,
        'NumPad5': 0x65,
        'NumPad6': 0x66,
        'NumPad7': 0x67,
        'NumPad8': 0x68,
        'NumPad9': 0x69,
        'MultiplyKey': 0x6A,
        'AddKey': 0x6B,
        'SeparatorKey': 0x6C,
        'SubtractKey': 0x6D,
        'DecimalKey': 0x6E,
        'DivideKey': 0x6F,
        'F1': 0x70,
        'F2': 0x71,
        'F3': 0x72,
        'F4': 0x73,
        'F5': 0x74,
        'F6': 0x75,
        'F7': 0x76,
        'F8': 0x77,
        'F9': 0x78,
        'F10': 0x79,
        'F11': 0x7A,
        'F12': 0x7B,
        'F13': 0x7C,
        'F14': 0x7D,
        'F15': 0x7E,
        'F16': 0x7F,
        'F17': 0x80,
        'F18': 0x81,
        'F19': 0x82,
        'F20': 0x83,
        'F21': 0x84,
        'F22': 0x85,
        'F23': 0x86,
        'F24': 0x87,
        'NumLock': 0x90,
        'ScrollLock': 0x91,
        'LeftShift': 0xA0,
        'RightShift ': 0xA1,
        'LeftControl': 0xA2,
        'RightControl': 0xA3,
        'LeftMenu': 0xA4,
        'RightMenu': 0xA5,
        'BrowserBack': 0xA6,
        'BrowserForward': 0xA7,
        'BrowserRefresh': 0xA8,
        'BrowserStop': 0xA9,
        'BrowserSearch': 0xAA,
        'BrowserFavorites': 0xAB,
        'BrowserStartAndHome': 0xAC,
        'VolumeMute': 0xAD,
        'VolumeDown': 0xAE,
        'VolumeUp': 0xAF,
        'NextTrack': 0xB0,
        'PreviousTrack': 0xB1,
        'StopMedia': 0xB2,
        'Play/PauseMedia': 0xB3,
        'StartMail': 0xB4,
        'SelectMedia': 0xB5,
        'StartApplication1': 0xB6,
        'StartApplication2': 0xB7,
        'AttnKey': 0xF6,
        'CrselKey': 0xF7,
        'ExselKey': 0xF8,
        'PlayKey': 0xFA,
        'ZoomKey': 0xFB,
        'ClearKey': 0xFE,
    };
    cef.cefCachePath = window.cefCachePath;
    cef.clientWorkDirectory = window.clientWorkDirectory;
    cef.currentClientVersion = window.currentClientVersion;
    cef.closeProcess = (pid) => {
        window[moduleName]['close_process'](pid);
    };
    cef.closeMedias = () => {
        Array.from(document.getElementsByTagName('video')).forEach(e => { e.pause(); e.currentTime = 0 });
        Array.from(document.getElementsByTagName('audio')).forEach(e => { e.pause(); e.currentTime = 0 });
    };
    cef.addEventListener = (eventName, eventHook) => {
        if (customEventMap[eventName] === undefined) {
            console.error(`window.${sdkModuleName}.addEventListener(eventName, eventHook) : eventName 必须是 ${Object.keys(customEventMap)} 中的一个`);
            return;
        }
        if (typeof eventHook !== 'function') {
            console.error(`window.${sdkModuleName}.addEventListener(eventName, eventHook): eventHook 必须是一个函数`);
            return;
        }
        customEventMap[eventName].hooks += 1;
        cef.hooks[eventName] = customEventMap[eventName].hooks;
        window.addEventListener(eventName, eventHook);
    };
    cef.removeEventListener = (eventName, eventHook) => {
        if (customEventMap[eventName] === undefined) {
            console.error(`window.${sdkModuleName}.addEventListener(eventName, eventHook) : eventName 必须是 ${Object.keys(customEventMap)} 中的一个`)
            return;
        }
        if (typeof eventHook !== 'function') {
            console.error(`window.${sdkModuleName}.addEventListener(eventName, eventHook): eventHook 必须是一个函数`);
            return;
        }
        customEventMap[eventName].hooks -= 1;
        cef.hooks[eventName] = customEventMap[eventName].hooks;
        window.removeEventListener(eventName, eventHook);
    };
    cef.show = (cid) => {
        if (window[moduleName] && typeof window[moduleName]['show_window'] === 'function') {
            window[moduleName]['show_window'](cid);
        }
    };
    cef.hide = (cid) => {
        cef.closeMedias();
        if (window[moduleName] && typeof window[moduleName]['hide_window'] === 'function') {
            window[moduleName]['hide_window'](cid);
        }
    };
    cef.open = (params) => {
        if (window[moduleName] && typeof window[moduleName].open === 'function') {
            window[moduleName].open(params);
        }
    };
    cef.reloadIgnoreCache = () => {
        if (window[moduleName] && typeof window[moduleName]['reload_ignore_cache'] === 'function') {
            window[moduleName]['reload_ignore_cache']();
        }
    };
    cef.close = (cidLists) => {
        cef.closeMedias();
        if (cidLists && Object.prototype.toString.call(cidLists) === '[object Array]') {
            if (window[moduleName] && typeof window[moduleName]['close_window'] === 'function') {
                window[moduleName]['close_window'](cidLists);
            }
        } else if (!cidLists) {
            if (window[moduleName] && typeof window[moduleName]['close_window'] === 'function') {
                window[moduleName]['close_window']();
            }
        } else {
            console.warn('__cef__.close(cidLists): cidLists 的值只能为 undefined 或者 array')
        }
    };
    cef.closeAll = () => {
        if (window[moduleName] && typeof window[moduleName]['close_all_window'] === 'function') {
            window[moduleName]['close_all_window']();
        }
    };
    cef.toggleFullScreen = () => {
        if (window[moduleName] && typeof window[moduleName]['toggle_full_screen'] === 'function') {
            window[moduleName]['toggle_full_screen']();
        }
    };
    cef.maximize = (uid) => {
        if (typeof uid === 'string') {
            if (window[moduleName] && typeof window[moduleName]['maximize_window'] === 'function') {
                window[moduleName]['maximize_window'](uid);
            }
        } else {
            if (window[moduleName] && typeof window[moduleName]['maximize_current_window'] === 'function') {
                window[moduleName]['maximize_current_window']();
            }
        }
    };
    cef.minimize = (uid) => {
        if (typeof uid === 'string') {
            if (window[moduleName] && typeof window[moduleName]['minimize_window'] === 'function') {
                window[moduleName]['minimize_window'](uid);
            }
        } else {
            if (window[moduleName] && typeof window[moduleName]['minimize_current_window'] === 'function') {
                window[moduleName]['minimize_current_window']();
            }
        }
    };
    cef.focus = (cid) => {
        if (window[moduleName] && typeof window[moduleName]['focus_browser'] === 'function') {
            window[moduleName]['focus_browser'](cid);
        }
    };
    cef.arouse = (cid) => {
        if (window[moduleName] && typeof window[moduleName]['arouse_window'] === 'function') {
            window[moduleName]['arouse_window'](cid);
        }
    };
    cef.setBrowserPayload = (cid, payload) => {
        if (typeof cid !== 'string' || cid === '') {
            console.error('__cef__.setBrowserPayload(cid ,payload): cid 必须为字符类型，且不为空字符串');
            return;
        }
        if (Object.prototype.toString.call(payload) !== '[object Object]') {
            console.error('__cef__.setBrowserPayload(cid ,payload): payload 必须为JsonObject');
            return;
        }
        if (window[moduleName] && typeof window[moduleName]['set_browser_payload'] === 'function') {
            window[moduleName]['set_browser_payload'](cid, payload);
        }

    };
    cef.broadCast = (eventData) => {
        if (eventData && Object.prototype.toString.call(eventData) !== '[object Object]') {
            console.error('__cef__.broadCast(eventData): eventData 为非必填项，如果传值，必须为Json Object');
            return;
        }
        if (window[moduleName] && typeof window[moduleName]['dispatch_customize_event'] === 'function') {
            window[moduleName]['dispatch_customize_event'](customEventMap.windowBroadcastEvent.name, eventData || {});
        }
    };
    cef.nestFrame = (params) => {
        if (params && Object.prototype.toString.call(params) !== '[object Object]') {
            console.error('__cef__.nestFrame(params): params 为非必填项，如果传值，必须为Json Object');
            return;
        }
        if (window[moduleName] && typeof window[moduleName]['nest_frame_window'] === 'function') {
            window[moduleName]['nest_frame_window'](params);
        }
    };
    cef.nestApplication = (params) => {
        if (!params || (params && Object.prototype.toString.call(params) !== '[object Object]')) {
            console.error('__cef__.nestApplication(params): params必须为Json Object');
            return;
        }
        if (window[moduleName] && typeof window[moduleName]['nest_third_party_application'] === 'function') {
            window[moduleName]['nest_third_party_application'](params);
        }
    };
    cef.refreshWindowGeometry = (cid) => {
        if (window[moduleName] && typeof window[moduleName]['update_window_geometry'] === 'function') {
            window[moduleName]['update_window_geometry'](cid);
        }
    };
    cef.showCloseDialog = (params) => {
        if (!params || (params && Object.prototype.toString.call(params) !== '[object Object]')) {
            console.error('__cef__.showCloseDialog(params): params必须为Json Object');
            return;
        }
        if (window[moduleName] && typeof window[moduleName]['show_close_dialog'] === 'function') {
            window[moduleName]['show_close_dialog'](params);
        }
    };
    cef.showDevTools = () => {
        if (window[moduleName] && typeof window[moduleName]['show_dev_tool'] === 'function') {
            window[moduleName]['show_dev_tool']();
        }
    };
    cef.setWindowTitle = (title) => {
        if (window[moduleName] && typeof window[moduleName]['set_window_title'] === 'function') {
            window[moduleName]['set_window_title'](title);
        }
    };
    cef.encryption = (code) => {
        return btoa(`${btoa(encryptionKey)}${btoa(code)}`)
    };
    cef.decryption = (code) => {
      const t_1 = atob(code);
      const t_2 = t_1.replace(btoa(encryptionKey), '');
      return atob(t_2);
    };
    cef.closeNestClient = (cid) => {
        if (window[moduleName] && typeof window[moduleName]['close_nest_client'] === 'function') {
            window[moduleName]['close_nest_client'](cid);
        }
    };
    cef.throwKeyEvent = (params) => {
        if (!params || (params && Object.prototype.toString.call(params) !== '[object Object]')) {
            console.error('__cef__.throwKeyEvent(params): params必须为Json Object');
            return;
        }
        if (window[moduleName] && typeof window[moduleName]['send_key_event_to_client'] === 'function') {
            window[moduleName]['send_key_event_to_client'](params);
        }
    };
    cef.setCurrentMenu = (params) => {
        if (params && Object.prototype.toString.call(params) === '[object String]') {
            window[moduleName]['set_menu_info'](params);
        }
    };
    cef.getCurrentMenu = () => {
        window[moduleName]['get_menu_info']();
    };
    cef.reloadUrlByCid = (cid, url) => {
        if (typeof cid !== 'string' || cid === '') {
            console.error('__cef__.reloadUrlByCid(cid ,url): cid 必须为字符类型，且不为空字符串');
            return;
        }
        if (typeof url !== 'string' || url === '') {
            console.error('__cef__.reloadUrlByCid(cid ,url): url 必须为字符类型，且不为空字符串');
            return;
        }
        if (window[moduleName] && typeof window[moduleName]['reload_url_by_cid'] === 'function') {
            window[moduleName]['reload_url_by_cid'](cid,url);
        }
    };
    cef.reloadUrl = (url) => {
        if (typeof url !== 'string' || url === '') {
            console.error('__cef__.reloadUrl(url): url 必须为字符类型，且不为空字符串');
            return;
        }
        if (window[moduleName] && typeof window[moduleName]['load_url'] === 'function') {
            window[moduleName]['load_url'](url);
        }
    };
    cef.virtualEvents = (selector,obj,key) => {
        class KeyEvent {
      // 初始化
      init(Input, obj,key) {
        this.InputVal = [] // 总长度
        this.InputDel = [] // 光标展示的长度
        this.CopyText = false // 是否已经复制过
        this.ctrlText = false // 是否已经选中过
        this.Input = Input
        this.copyValue = [] // 存储复制的值
        this.timer = null
        this.timerClick = null // 点击与双击
        this.selectionStart = null
        this.selectionEnd = null
        this.vm = obj || {}
        this.startArry = []
        this.endArry = []
        this.index = 0
        this.empty = false
		this.divSpan=this.Input.id+'div'
        let self = this
        if (
          this.Input === null ||
          this.Input === undefined ||
          this.Input.nodeName.toLocaleUpperCase() !== 'INPUT'
        ) {
          return false
        }
        this.height = this.Input.offsetHeight || 0
        //  input 包裹节点
        if (document.querySelector("#"+this.divSpan) === null) {
          this.parseSpan()
        }
        //  键盘按下，失去焦点，点击事件
        this.Input.setAttribute('readonly', 'true')

        this.Input.addEventListener('keydown', event => {
        if(!this.em){
            return false;
        }
        if (this.Input.value.length < 1) {
            this.InputVal = []
            this.vm.goodsValue = ''
			this.vm[key]=''
          }
          if (event.keyCode === 8) {
            this.caseCode(event)
          }
        })
        document.addEventListener('keydown', event => {
            if(!this.em){
                return false;
            }
          if (this.Input.value.length < 1) {
            this.InputVal = []
            this.vm.goodsValue = ''
			this.vm[key]=''

          }
          if (document.activeElement === this.Input) {
              if(event.keyCode!==8){
                this.caseCode(event)
              }
          }
        })
        this.Input.addEventListener('click', event => {
            if(!this.em){
                return false;
            }
          this.index = 1
          clearTimeout(this.timerClick)
          this.timerClick = setTimeout(() => {
            if (
              window.getSelection().toString() !== '' &&
              window.getSelection().anchorNode.id === this.divSpan
            ) {
              if (this.InputVal.length > 0) {
                this.em.style.display = 'none'
                this.selectionStart = this.Input.selectionStart
                this.selectionEnd = this.Input.selectionEnd
                this.startArry = this.InputVal.slice(0, this.selectionStart)
                this.endArry = this.InputVal.slice(
                  this.selectionEnd,
                  this.InputVal.length
                )
                this.selectionStart = 0
                this.selectionEnd = 0
              } else {
                this.startArry = []
                this.endArry = []
                this.InputVal = []
              }
              this.cursorTime('false')
            } else {
              this.em.style.display = 'inline-block'
              this.keyboard('dwon', event.key)
            }
          }, 300)
          this.Input.blur()
          this.Input.focus()
        })
        this.Input.addEventListener('focus', event => {
            if(!this.em){
                return false;
            }
          if (this.Input.value.length < 1) {
            this.InputVal = []
            this.vm.goodsValue = ''
			this.vm[key]=''
            this.index=1;
          }else{
              this.Input.value=this.vm[key];
            this.InputVal =this.Input.value.split('');
            this.InputDel =this.Input.value.split('');

          }
          this.Input.style.border = '1px solid #2A5596'
          this.em.style.display = 'inline-block'
          this.keyboard('dwon', event.key)
          // this.cursorTime('true');
        })
        this.Input.addEventListener('dblclick', event => {
          clearTimeout(this.timerClick)
          event.stopPropagation()
          if (this.Input.selectionEnd !== 0) {
            this.Input.select()
          }
          this.cursorTime('false')
          this.ctrlText = true
        })
        this.Input.addEventListener('blur', event => {
          this.Input.style.border = '1px solid #BEBEBE'
          this.Input.selectionStart = 0
          this.index = 0
          this.cursorTime('false')
        })
        this.Input.addEventListener('paste', event => {
          let clipboardData = event.clipboardData.getData('Text').split('')
          this.copyValue = true
          this.copyValue = [...clipboardData]
          event.stopPropagation()
          if (this.CopyText === false) {
            this.ctrlvHtml()
          }
        })
      }
      // 复制黏贴内容
      ctrlvHtml() {
        if (
          this.startArry.length > 0 ||
          this.endArry.length > 0 ||
          (window.getSelection().toString() !== '' &&
            window.getSelection().anchorNode.id === this.divSpan)
        ) {
          window.getSelection().empty()
          this.InputVal = [
            ...this.startArry,
            ...this.copyValue,
            ...this.endArry
          ]
          this.InputDel = [...this.startArry, ...this.copyValue]
          this.startArry = []
          this.endArry = []
        } else {
          if (this.Input.value < 1) {
            this.InputVal = [...this.copyValue]
            this.InputDel = [...this.InputVal]
          } else {
            if (this.InputVal.length !== this.InputDel.length) {
              let start = this.InputDel.length
              let end = this.InputVal.length
              let InputStart = this.InputVal.slice(0, start)
              let InputEnd = this.InputVal.slice(start, end)
              this.InputVal = [...InputStart, ...this.copyValue, ...InputEnd]
              this.InputDel = [...this.InputDel, ...this.copyValue]
              this.em.style.display = 'inline-block'
              this.cursorTime('true')
              let spanHtml = [...this.InputDel]
              this.spanLeft(spanHtml)
              this.ctrlText = false
              return false
            } else {
              this.InputVal = [...this.InputVal, ...this.copyValue]
              this.InputDel = [...this.InputVal]
            }
          }
        }
        let spanHtml = [...this.InputDel]
        this.em.style.display = 'inline-block'
        this.cursorTime('true')

        this.spanLeft(spanHtml)
        this.ctrlText = false
        return false
      }
      // 添加div和span 光标
      parseSpan() {
        this.wrapOuter(
          this.Input,
          "<div id='"+this.divSpan+"' style='position: relative;'></div>"
        )
        this.span = document.createElement('span')
        this.em = document.createElement('em')
        this.span.className = 'wrapCurr'
        let font = getComputedStyle(this.Input).font
        let letterSpacing = getComputedStyle(this.Input).letterSpacing
        this.paddingLeft =
          parseFloat(getComputedStyle(this.Input).paddingLeft) || 0
        let height = parseInt(getComputedStyle(this.Input).fontSize)
        let margin = getComputedStyle(this.Input).margin
        let span_Top =
          Math.floor((Number(this.height) - parseInt(height)) / 2) +
          parseInt(getComputedStyle(this.Input).paddingTop)
        this.span.style.cssText = `position: absolute; z-index: -1;left: ${
          this.paddingLeft
        }px;letter-spacing:${letterSpacing}; top: ${span_Top}px; margin:${margin};font:${font};height:${height}px; color: transparent; background: transparent; overflow: hidden;white-space: nowrap`
        this.em.style.cssText = `position: absolute;left: ${
          this.paddingLeft
        }px; top: ${span_Top}px; margin:${margin};display:none;font:${font};height:${height}px;border-left: 1px solid black; `
        document.querySelector("#"+this.divSpan).appendChild(this.span)
        document.querySelector("#"+this.divSpan).appendChild(this.em)
      }
      // 虚拟dom
      parseHTML(str) {
        if (document.createRange) {
          let range = document.createRange()
          range.setStartAfter(document.body)
          return range.createContextualFragment(str)
        } else {
          return document.createElement(str)
        }
      }
      // 包裹节点代码
      wrapOuter(target, html) {
        let wrap = this.parseHTML(html)
        target.parentNode.insertBefore(wrap, target)
        target.previousSibling.appendChild(target)
      }
      //  键盘keyCode  事件
      caseCode(event) {
        let self = this
        switch (event.keyCode) {
          case 8: {
            this.keyboard('del', event.key)
            break
          }
          case 46: {
            this.keyboard('del', event.key)
            break
          }
          case 13: {
            this.InputDel = []
            this.spanLeft([])
            break
          }
          case 38: {
            //this.keyboard('up', event.key)
            break
          }
          case 39: {
            if (this.InputVal.length !== this.InputDel.length) {
              this.keyboard('back', event.key)
            }

            break
          }
          case 37: {
            if (this.InputDel.length > 0) {
              this.keyboard('go', event.key)
            }

            break
          }
          case 40:
            //this.keyboard('dwon', event.key)
            break
          default: {
            if (
              (event.ctrlKey || event.altKey || event.metaKey) &&
              event.keyCode
            ) {
              this.cursorTime('true')
              if (event.ctrlKey === true && event.keyCode === 65) {
                this.ctrlText = true
              } else if (event.ctrlKey === true && event.keyCode === 67) {
                this.CopyText = true

                if (
                  window.getSelection().toString() !== '' &&
                  window.getSelection().anchorNode.id === 'wrapSpan'
                ) {
                  this.copyValue = []
                  this.copyValue.push(window.getSelection().toString())
                } else {
                  this.copyValue = [...this.InputVal]
                }
                document.execCommand('Copy')
              } else if (event.ctrlKey === true && event.keyCode === 88) {
                this.CopyText = true
                this.copyValue = [...this.InputVal]
                this.InputDel = []
                this.InputVal = []
                this.cursorTime('true')
                document.execCommand('Copy')
                this.spanLeft([''])
              } else if (event.ctrlKey === true && event.keyCode === 86) {
                if (this.CopyText) {
                  event.stopPropagation()
                  this.ctrlvHtml()
                }
              }
              return false
            } else {
              let stringKey =
                '-1234567890qwertyuiopasdfghjklzxcvbnnmQWERTYUIOPASDFGHJKLZXCVBNM'
              if (stringKey.indexOf(event.key) !== -1) {
                this.keyboard('true', event.key)
                this.cursorTime('true')
              }
              /* if(event.keyCode>47 && event.keyCode<58 || event.keyCode>64 && event.keyCode<91 || event.keyCode>185 && event.keyCode<230 || event.keyCode>95 && event.keyCode<112){
                            this.keyboard('true', event.key);
                            this.cursorTime('true');
                        }else{
                            this.cursorTime('false');
                        }*/
            }
          }
        }
      }
      //  键盘上下键及Back键
      keyboard(type, key) {
        let spanHtml = []
        if (type === 'true') {
          if (
            this.startArry.length > 0 ||
            this.endArry.length > 0 ||
            (window.getSelection().toString() !== '' &&
              window.getSelection().anchorNode.id === 'wrapSpan')
          ) {
            this.InputVal = [...this.startArry, key, ...this.endArry]
            this.InputDel = [...this.startArry, key]
            spanHtml = [...this.InputDel]
            this.selectionStart = null
            this.selectionEnd = null
            this.startArry = []
            this.endArry = []
            window.getSelection().removeAllRanges()
          } else {
            if (this.InputDel.length === this.InputVal.length) {
              if (this.ctrlText === true) {
                this.InputVal = []
                this.InputDel = []
                spanHtml = []
                this.ctrlText = false
                this.selectionStart = null
                this.selectionEnd = null
                this.startArry = []
                this.endArry = []
              }
              this.InputVal.push(key)
              this.InputDel = [...this.InputVal]
              spanHtml = [...this.InputVal]
            } else {
              this.InputVal.splice(this.InputDel.length, 0, key)
              this.InputDel.push(key)
              spanHtml = [...this.InputDel]
            }
          }
        } else if (type === 'del') {
          if (this.InputVal.length > 0) {
            if (
              this.ctrlText === true ||
              (this.Input.selectionStart === 0 &&
                this.Input.selectionEnd === this.InputVal.length)
            ) {
              this.InputVal = []
              this.InputDel = []
              this.startArry = []
              this.endArry = []
              spanHtml = []
              this.ctrlText = false
            } else if (
              this.startArry.length > 0 ||
              this.endArry.length > 0 ||
              (window.getSelection().toString() !== '' &&
                window.getSelection().anchorNode.id === 'wrapSpan')
            ) {
              this.InputVal = [...this.startArry, ...this.endArry]
              this.InputDel = [...this.startArry]
              spanHtml = [...this.InputDel]
              this.selectionStart = null
              this.selectionEnd = null
              this.startArry = []
              this.endArry = []
            } else {
              if (
                this.InputDel.length !== this.InputVal.length &&
                this.InputDel.length > 0
              ) {
                this.InputVal.splice(this.InputDel.length - 1, 1)
                this.InputDel = this.InputDel.splice(
                  0,
                  this.InputDel.length - 1
                )
                spanHtml = [...this.InputDel]
              } else if (this.InputDel.length > 0) {
                this.InputVal = this.InputVal.splice(
                  0,
                  this.InputVal.length - 1
                )
                spanHtml = [...this.InputVal]
                this.InputDel = [...this.InputVal]
              }
            }
          }
        } else if (type === 'up') {
          this.InputDel = []
          this.Input.selectionEnd = 0
          this.Input.value = this.InputVal.join('')
          spanHtml = [...this.InputDel]
        } else if (type === 'dwon') {
          this.Input.selectionEnd = 0
          this.InputDel = [...this.InputVal]
          spanHtml = [...this.InputVal]
        } else if (type === 'back') {
          this.Input.selectionEnd = 0
          this.InputDel.push(this.InputVal[this.InputDel.length])
          spanHtml = [...this.InputDel]
        } else if (type === 'go') {
          this.Input.selectionEnd = 0
          this.InputDel = this.InputDel.splice(0, this.InputDel.length - 1)
          spanHtml = [...this.InputDel]
        }
        this.spanLeft(spanHtml)
      }
      //  计算文本宽度
      spanLeft(spanHtml) {
        this.em.style.display = 'inline-block'
        this.cursorTime('true')
        this.span.innerHTML = spanHtml.join('')
        this.Input.value = this.InputVal.join('')
        this.vm.goodsValue = this.InputVal.join('')
		this.vm[key]=this.InputVal.join('')

        this.left = this.span.offsetWidth + this.paddingLeft
        this.offsetWidth = this.span.offsetWidth
        this.span.style.left = 0 - this.span.offsetWidth + 'px'
        if (
          this.InputVal.length > 0 &&
          this.InputVal.length === this.InputDel.length
        ) {
          this.em.style.left = this.left + 2 + 'px'
        } else {
          this.em.style.left = this.left + 'px'
        }
        this.Input.style.textIndent = '0px'
        if (this.left > this.Input.offsetWidth - 3) {
          if (this.Input.offsetWidth - this.offsetWidth < 2) {
            this.Input.style.textIndent =
              this.Input.offsetWidth - this.left - 3 + 'px'
          } else {
            this.Input.style.textIndent = '0px'
          }
          this.em.style.left = this.Input.offsetWidth - 3 + 'px'
        }
      }

      //  光标事件
      cursorTime(code) {
        let self = this
        if(!this.em){
            return false;
        }
        if (code === 'true') {
          clearInterval(self.timer)
		  if(!self.em){
			  return false;
		  }
          self.em.style.display = 'inline-block'
          self.timer = setInterval(() => {
            if (self.em.style.display != 'none') {
              self.em.style.display = 'none'
            } else {
              self.em.style.display = 'inline-block'
            }
          }, 500)
        } else {
          self.em.style.display = 'none'
          clearInterval(self.timer)
        }
      }
    }

		const _Key = new KeyEvent()
		return _Key.init(selector, obj,key)
    };
    cef.CEF_INFO = {};
    window[sdkModuleName] = cef;
    window[pythonCallBack] = python_cef;
    window.CEF_HAS_INITIALIZED = true;
}());"""
