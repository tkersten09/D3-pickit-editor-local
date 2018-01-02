const { app, BrowserWindow, ipcMain } = require('electron');
const url = require('url');
const path = require('path');
const isDev = require('electron-is-dev');
const childProcess = require('child_process');
const ProgressBar = require('electron-progressbar');

if (isDev) {
  require('electron-debug')({ showDevTools: true });
}

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
  const p = path.join(__dirname, PY_FOLDER, 'lib', `${PY_MODULE}.py`);
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
    pyProc = childProcess.execFile(script, [port]);
  } else {
    console.log(`run script: ${script}`);
    pyProc = childProcess.spawn('python', [script, port]);
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
  mainWindow.loadURL(url.format({
    pathname: path.join(__dirname, 'gui', 'browser.html'),
    protocol: 'file:',
    slashes: true,
  }));

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
};

const addModalCreateEvent = () => {
  // Add event that creates the modal window
  mainWindow.webContents.on(
    'new-window',
    (
      event,
      urlNewWindow,
      frameName,
      disposition,
      options,
      additionalFeatures,
    ) => {
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

const addProgressBarEvent = () => {
  mainWindow.webContents.on('new-progressbar', (event, maxValue) => {
    console.log('[main.js] new-progrssbar event')
    // Add event that creates the modal window
    const progressBar = new ProgressBar({
      closeOnComplete: false,
      indeterminate: false,
      text: 'Fetching Builds...',
      maxValue,
      browserWindow: {
        parent: mainWindow,
      },
    });

    progressBar
      .on('progress', (value) => {
        progressBar.detail = `${value} of ${
          progressBar.getOptions().maxValue
        } Builds.`;
      })
      .on('completed', (value) => {
        clearInterval(interval);
        progressBar.detail = 'Completed. Exiting...';

        setTimeout(() => {
          progressBar.close();
        }, 1500);
      })
      .on('aborted', (value) => {
        console.info(`aborted on Build ${value}/${progressBar.getOptions().maxValue}`);
      });
  });
};

app.on('ready', () => {
  ipcMain.on('closeModal', () => {
    if (modal) {
      modal.close();
    }
  });
  createWindow();
  addModalCreateEvent();
  if (isDev) {
    const elemon = require('elemon'); // require elemon if electron is in dev
    elemon({
      app,
      mainFile: 'main.js',
      bws: [
        { bw: mainWindow, res: ['browser.html', 'browser.js', 'browser.css'] },
        { bw: modal, res: [] },
      ],
    });
  }
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
