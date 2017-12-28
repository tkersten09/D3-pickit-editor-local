const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

console.log('main.js is here');
/** ***********************************************************
 * py process
 ************************************************************ */

// const PY_DIST_FOLDER = 'lib'
const PY_FOLDER = 'pickit_cl';
const PY_MODULE = 'api'; // without .py suffix

let pyProc = null;
let pyPort = null;

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
const guessPackaged = () => false;

const getScriptPath = () => {
  // if (process.platform === 'win32') {
  //   return path.join(__dirname, PY_FOLDER, PY_MODULE + '.exe')
  // }
  p = path.join(__dirname, PY_FOLDER, 'lib', `${PY_MODULE}.py`);
  console.log(`script path: ${p}`);
  return p;
};

const selectPort = () => {
  pyPort = 4242;
  return pyPort;
};

const createPyProc = () => {
  const script = getScriptPath();
  const port = `${selectPort()}`;

  if (guessPackaged()) {
    console.log(`exec script: ${script}`);
    pyProc = require('child_process').execFile(script, [port]);
  } else {
    console.log(`run script: ${script}`);
    pyProc = require('child_process').spawn('python', [script, port]);
  }

  if (pyProc != null) {
    // console.log(pyProc)
    console.log(`child process success on port ${port}`);
  }
};

const exitPyProc = () => {
  pyProc.kill();
  pyProc = null;
  pyPort = null;
};

app.on('ready', createPyProc);
app.on('will-quit', exitPyProc);

/** ***********************************************************
 * window management
 ************************************************************ */

let mainWindow = null;
let modal = null;

const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nativeWindowOpen: true,
    },
  });
  mainWindow.loadURL(require('url').format({
    pathname: path.join(__dirname, 'gui', 'browser.html'),
    protocol: 'file:',
    slashes: true,
  }));
  mainWindow.webContents.openDevTools();
  console.error('Window created');
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
};

const addModalCreateEvent = () => {
  // Add event that creates the modal window
  mainWindow.webContents.on(
    'new-window',
    (event, url, frameName, disposition, options, additionalFeatures) => {
      if (frameName === 'modal') {
        event.preventDefault();
        Object.assign(options, {
          show: false,
          modal: true,
          parent: mainWindow,
          width: 250,
          height: 155,
          center: true,
        });
        modal = new BrowserWindow(options);
        modal.on('closed', () => {
          modal = null;
        });
        event.newGuest = modal;
      }
    },
  );
};

app.on('ready', () => {
  ipcMain.on('closeModal', () => {
    if (modal) {
      modal.close();
    }
  });
  createWindow();
  addModalCreateEvent();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});
