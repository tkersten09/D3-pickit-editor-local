const {app, BrowserWindow} = require('electron');
const path = require('path')

/*************************************************************
 * py process
 *************************************************************/

// const PY_DIST_FOLDER = 'lib'
const PY_FOLDER = 'lib'
const PY_MODULE = 'api' // without .py suffix

let pyProc = null
let pyPort = null

// const guessPackaged = () => {
//   const fullPath = path.join(__dirname, PY_DIST_FOLDER)
//   return require('fs').existsSync(fullPath)
// }

// const getScriptPath = () => {
//   if (!guessPackaged()) {
//     return path.join(__dirname, PY_FOLDER, PY_MODULE + '.py')
//   }
//   if (process.platform === 'win32') {
//     return path.join(__dirname, PY_DIST_FOLDER, PY_MODULE, PY_MODULE + '.exe')
//   }
//   return path.join(__dirname, PY_DIST_FOLDER, PY_MODULE, PY_MODULE)
// }
const guessPackaged = () => {
  return false
}

const getScriptPath = () => {
  // if (process.platform === 'win32') {
  //   return path.join(__dirname, PY_FOLDER, PY_MODULE + '.exe')
  // }
  p = path.join(__dirname, PY_FOLDER, PY_MODULE + '.py')
  console.log('script path: ' + p)
  return p
}


const selectPort = () => {
  pyPort = 4242
  return pyPort
}

const createPyProc = () => {
  let script = getScriptPath()
  let port = '' + selectPort()

  if (guessPackaged()) {
    console.log('exec script: ' + script)
    pyProc = require('child_process').execFile(script, [port])
  } else {
    console.log('run script: ' + script)
    pyProc = require('child_process').spawn('python', [script, port])
  }

  if (pyProc != null) {
    //console.log(pyProc)
    console.log('child process success on port ' + port)
  }
}

const exitPyProc = () => {
  pyProc.kill()
  pyProc = null
  pyPort = null
}

// app.on('ready', createPyProc)
// app.on('will-quit', exitPyProc)


/*************************************************************
 * window management
 *************************************************************/

let mainWindow = null

const createWindow = () => {
  mainWindow = new BrowserWindow({width: 800, height: 600})
  mainWindow.loadURL(require('url').format({
    pathname: path.join(__dirname, 'browser.html'),
    protocol: 'file:',
    slashes: true
  }))
  // mainWindow.webContents.openDevTools()

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.on('ready', createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
})
