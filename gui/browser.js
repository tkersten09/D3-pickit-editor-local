/* eslint no-console: ["error", { allow: ["warn", "error"] }] */

const Console = console;
const path = require('path');
const fs = require('fs');
const url = require('url');
const { ipcRenderer } = require('electron');
const zerorpc = require('zerorpc');

function doLayout() {
  const webview = document.querySelector('webview');
  const controls = document.querySelector('#controls');
  const controlsHeight = controls.offsetHeight;
  const windowWidth = document.documentElement.clientWidth;
  const windowHeight = document.documentElement.clientHeight;
  const webviewWidth = windowWidth;
  const webviewHeight = windowHeight - controlsHeight;

  webview.style.width = `${webviewWidth}px`;
  webview.style.height = `${webviewHeight}px`;

  const sadWebview = document.querySelector('#sad-webview');
  sadWebview.style.width = `${webviewWidth}px`;
  sadWebview.style.height = `${webviewHeight * (2 / 3)}px`;
  sadWebview.style.paddingTop = `${webviewHeight / 3}px`;
}

const showModal = (fileName) => {
  const urlModal = url.format({
    pathname: path.join(__dirname, 'modal', `${fileName}.html`),
    protocol: 'file:',
    slashes: true,
  });
  const modal = window.open(urlModal, 'modal');
  const browserWindow = modal.require('electron').remote.getCurrentWindow();
  browserWindow.center();
  Console.log(browserWindow);
  // browserWindow.webContents.on('did-start-loading', (event) => {
  //   Console.log('[browser.js: modal] did-start-loading.');
  //   Console.log(event);
  // });
  // browserWindow.webContents.on('did-stop-loading', (event) => {
  //   Console.log('[browser.js: modal] did-stop-loading.');
  //   Console.log(event);
  // });

  browserWindow.webContents.on('dom-ready', () => {
    Console.log('[browser.js: modal] dom-ready.');

    const sc = modal.document.createElement('script');
    res = fs.readFileSync('gui/modal/renderer.js');
    sc.innerHTML = res;
    modal.document.querySelector('head').append(sc);

    Console.log('ok Button');
    const okButton = modal.document.querySelector('button.ok');
    okButton.addEventListener('click', () => {
      // modal.close() or browserWindow.close() doesn't work now
      ipcRenderer.send('closeModal');
    });
  });
  browserWindow.on('ready-to-show', () => {
    Console.log('[browser.js: modal] ready-to-show show().');
    setTimeout(() => {
      browserWindow.show();
    }, 500);
  });
};

window.onresize = doLayout;
let isLoading = false;
Console.log('[browser.js] is here');

// Bug fix with heatbeat timeout: https://stackoverflow.com/questions/23722757/python-node-zerorpc-heartbeat-error
const oClient = Object();
oClient.heartbeatInterval = 100000;

const client = new zerorpc.Client(oClient);

client.connect('tcp://127.0.0.1:4242');

const o = Object();
o.timeout = 1000;

client.invoke(o, 'echo', 'server ready', (error, res) => {
  if (error || res !== 'server ready') {
    console.error(`echo: ${error}`);
  } else {
    Console.log('server is ready');
  }
});

function strMapToObj(strMap) {
  const obj = Object.create(null);
  for (const [k, v] of strMap) {
    // We don’t escape the key '__proto__'
    // which can cause problems on older engines
    obj[k] = v;
  }
  return obj;
}
function strMapToJson(strMap) {
  return JSON.stringify(strMapToObj(strMap));
}

onload = function onload() {
  const webview = document.querySelector('webview');
  doLayout();

  client.invoke(o, 'init', (error, res) => {
    if (error) {
      console.error(error);
    } else {
      Console.log('[browser.js] init');
      const fn = url.format({
        pathname: path.join(__dirname, 'init.html'),
        protocol: 'file:',
        slashes: true,
      });
      Console.log(fn);
      navigateTo(fn);
      // webview.loadURL(fn);
      // webview.src = fn;
    }
  });

  function updateClass(className) {
    client.invoke(o, 'change_class', className, (error, res) => {
      if (error) {
        console.error(error);
      } else {
        Console.log('[browser.js] change_class');
        const fn = url.format({
          pathname: path.join(__dirname, 'temp', `${className}.html`),
          protocol: 'file:',
          slashes: true,
        });
        // console.error(fn)
        // let f = fs.openSync('gui\init.html', "w+")
        fs.writeFile(
          `C:/Users/Thomas/Documents/GitHub/pickit-cl/gui/temp/${className}.html`,
          res,
          (error2, res2) => {
            if (error2) {
              console.error(error2);
            }
            Console.log(`[browser.js] writeFile ${res2}`);
            Console.log(fn);
            // Console.log(res)
            // webview.loadURL('data:text/html;charset=utf-8,' + encodeURI(res))
            // webview.loadURL(fn);
            navigateTo(fn);
          },
        );
      }
    });
  }
  updateClass('crusaider');

  ipcRenderer.on('newSelection', (event, className, newSelectionJson) => {
    Console.log('[browser.js] className: ');
    Console.log(className);
    Console.log('[browser.js] newSelectionJson:');
    Console.log(newSelectionJson);
    client.invoke('update', className, newSelectionJson, (error, res) => {
      if (error) {
        console.error(`[browser.js] error invoke update: ${error}`);
      } else {
        Console.log(`[browser.js] invoke update: ${res}`);
      }
    });
  });

  ipcRenderer.on('navigateTo', (event, className) => {
    Console.log('[browser.js] navigateTo className: ');
    Console.log(className);
    updateClass(className);
  });

  webview.addEventListener('dom-ready', () => {
    webview.openDevTools();
    Console.log('[browser.js] dom-ready');
  });

  document.querySelector('#export_build_numbers').onclick = function invokeExport() {
    client.invoke(o, 'export_build_numbers', (error, res) => {
      if (error) {
        Console.error(`echo: ${error}`);
      } else {
        Console.log(`[browser.js] invoke export_build_numbers: ${res}`);
        showModal('modal_build_numbers');
      }
    });
  };

  document.querySelector('#export_pickit_config').onclick = function invokeExport() {
    client.invoke(o, 'export_pickit_config', 3, 'build', (error, res) => {
      if (error) {
        Console.error(`echo: ${error}`);
      } else {
        Console.log(`[browser.js] invoke export_pickit_config: ${res}`);
        showModal('modal_pickit');
      }
    });
  };

  document.querySelector('#back').onclick = function onGoBack() {
    webview.goBack();
  };

  document.querySelector('#forward').onclick = function () {
    webview.goForward();
  };

  document.querySelector('#home').onclick = function () {
    navigateTo('http://www.github.com/');
  };

  document.querySelector('#reload').onclick = function () {
    if (isLoading) {
      webview.stop();
    } else {
      webview.reload();
    }
  };
  document
    .querySelector('#reload')
    .addEventListener('webkitAnimationIteration', () => {
      if (!isLoading) {
        document.body.classList.remove('loading');
      }
    });

  document.querySelector('#location-form').onsubmit = function (e) {
    e.preventDefault();
    navigateTo(document.querySelector('#location').value);
  };

  webview.addEventListener('close', handleExit);

  webview.addEventListener('load-commit', handleLoadCommit);
  webview.addEventListener('did-navigate-in-page', handleNavigateInPage);
  // webview.addEventListener('update-target-url', handleUpdateURL);
  webview.addEventListener('will-navigate', handleNavigateStart);
  webview.addEventListener('did-start-loading', handleLoadStart);
  webview.addEventListener('did-stop-loading', handleLoadStop);
  webview.addEventListener('did-fail-load', handleLoadAbort);
  webview.addEventListener('did-get-redirect-request', handleLoadRedirect);
  webview.addEventListener('did-finish-load', handleDidFinishLoad);

  //   // Test for the presence of the experimental <webview> zoom and find APIs.
  //   if (
  //     typeof webview.setZoom === 'function' &&
  //     typeof webview.find === 'function'
  //   ) {
  //     let findMatchCase = false;
  //
  //     document.querySelector('#zoom').onclick = function toggleZoom() {
  //       if (document.querySelector('#zoom-box').style.display == '-webkit-flex') {
  //         closeZoomBox();
  //       } else {
  //         openZoomBox();
  //       }
  //     };
  //
  //     document.querySelector('#zoom-form').onsubmit = function submitZoom(e) {
  //       e.preventDefault();
  //       const zoomText = document.forms['zoom-form']['zoom-text'];
  //       let zoomFactor = Number(zoomText.value);
  //       if (zoomFactor > 5) {
  //         zoomText.value = '5';
  //         zoomFactor = 5;
  //       } else if (zoomFactor < 0.25) {
  //         zoomText.value = '0.25';
  //         zoomFactor = 0.25;
  //       }
  //       webview.setZoom(zoomFactor);
  //     };
  //
  //     document.querySelector('#zoom-in').onclick = function zoomIn(e) {
  //       e.preventDefault();
  //       increaseZoom();
  //     };
  //
  //     document.querySelector('#zoom-out').onclick = function zoomOut(e) {
  //       e.preventDefault();
  //       decreaseZoom();
  //     };
  //
  //     document.querySelector('#find').onclick = function find() {
  //       if (document.querySelector('#find-box').style.display === 'block') {
  //         document.querySelector('webview').stopFinding();
  //         closeFindBox();
  //       } else {
  //         openFindBox();
  //       }
  //     };
  //
  //     document.querySelector('#find-text').oninput = function (e) {
  //       webview.find(document.forms['find-form']['find-text'].value, {
  //         matchCase: findMatchCase,
  //       });
  //     };
  //
  //     document.querySelector('#find-text').onkeydown = function (e) {
  //       if (event.ctrlKey && event.keyCode == 13) {
  //         e.preventDefault();
  //         webview.stopFinding('activate');
  //         closeFindBox();
  //       }
  //     };
  //
  //     document.querySelector('#match-case').onclick = function (e) {
  //       e.preventDefault();
  //       findMatchCase = !findMatchCase;
  //       const matchCase = document.querySelector('#match-case');
  //       if (findMatchCase) {
  //         matchCase.style.color = 'blue';
  //         matchCase.style['font-weight'] = 'bold';
  //       } else {
  //         matchCase.style.color = 'black';
  //         matchCase.style['font-weight'] = '';
  //       }
  //       webview.find(document.forms['find-form']['find-text'].value, {
  //         matchCase: findMatchCase,
  //       });
  //     };
  //
  //     document.querySelector('#find-backward').onclick = function (e) {
  //       e.preventDefault();
  //       webview.find(document.forms['find-form']['find-text'].value, {
  //         backward: true,
  //         matchCase: findMatchCase,
  //       });
  //     };
  //
  //     document.querySelector('#find-form').onsubmit = function (e) {
  //       e.preventDefault();
  //       webview.find(document.forms['find-form']['find-text'].value, {
  //         matchCase: findMatchCase,
  //       });
  //     };
  //
  //     webview.addEventListener('findupdate', handleFindUpdate);
  //     window.addEventListener('keydown', handleKeyDown);
  //   } else {
  //     const zoom = document.querySelector('#zoom');
  //     const find = document.querySelector('#find');
  //     zoom.style.visibility = 'hidden';
  //     zoom.style.position = 'absolute';
  //     find.style.visibility = 'hidden';
  //     find.style.position = 'absolute';
  //   }

  const zoom = document.querySelector('#zoom');
  const find = document.querySelector('#find');
  zoom.style.visibility = 'hidden';
  zoom.style.position = 'absolute';
  find.style.visibility = 'hidden';
  find.style.position = 'absolute';
};

function navigateTo(url) {
  resetExitedState();
  document.querySelector('webview').src = url;
}

function handleExit(event) {
  Console.log(event.type);
  document.body.classList.add('exited');
  if (event.type == 'abnormal') {
    document.body.classList.add('crashed');
  } else if (event.type == 'killed') {
    document.body.classList.add('killed');
  }
}

function resetExitedState() {
  document.body.classList.remove('exited');
  document.body.classList.remove('crashed');
  document.body.classList.remove('killed');
}

function handleFindUpdate(event) {
  const findResults = document.querySelector('#find-results');
  if (event.searchText == '') {
    findResults.innerText = '';
  } else {
    findResults.innerText = `${event.activeMatchOrdinal} of ${
      event.numberOfMatches
    }`;
  }

  // Ensure that the find box does not obscure the active match.
  if (event.finalUpdate && !event.canceled) {
    const findBox = document.querySelector('#find-box');
    findBox.style.left = '';
    findBox.style.opacity = '';
    const findBoxRect = findBox.getBoundingClientRect();
    if (findBoxObscuresActiveMatch(findBoxRect, event.selectionRect)) {
      // Move the find box out of the way if there is room on the screen, or
      // make it semi-transparent otherwise.
      const potentialLeft = event.selectionRect.left - findBoxRect.width - 10;
      if (potentialLeft >= 5) {
        findBox.style.left = `${potentialLeft}px`;
      } else {
        findBox.style.opacity = '0.5';
      }
    }
  }
}

function findBoxObscuresActiveMatch(findBoxRect, matchRect) {
  return (
    findBoxRect.left < matchRect.left + matchRect.width &&
    findBoxRect.right > matchRect.left &&
    findBoxRect.top < matchRect.top + matchRect.height &&
    findBoxRect.bottom > matchRect.top
  );
}

function handleKeyDown(event) {
  if (event.ctrlKey) {
    switch (event.keyCode) {
      // Ctrl+F.
      case 70:
        event.preventDefault();
        openFindBox();
        break;

      // Ctrl++.
      case 107:
      case 187:
        event.preventDefault();
        increaseZoom();
        break;

      // Ctrl+-.
      case 109:
      case 189:
        event.preventDefault();
        decreaseZoom();
    }
  }
}

function handleDidFinishLoad() {
  Console.log('[browser.js: event] load finished.');
  resetExitedState();
  const webview = document.querySelector('webview');
  document.querySelector('#location').value = webview.getURL();
  document.querySelector('#back').disabled = !webview.canGoBack();
  document.querySelector('#forward').disabled = !webview.canGoForward();
  closeBoxes();
}

function handleNavigateInPage(event) {
  Console.log('[browser.js: event] NavigateInPage.');
  Console.log(event);
}

function handleLoadCommit(event) {
  Console.log('[browser.js: event] LoadCommit.');
  Console.log(event);
}

function handleLoadStart(event) {
  const webview = document.querySelector('webview');
  Console.log('[browser.js: event] load start.');
  Console.log(event);
  document.body.classList.add('loading');
  isLoading = true;

  resetExitedState();
  document.querySelector('#location').value = webview.getURL();

  // document.querySelector('#location').value = event.url;
}

function handleNavigateStart(event) {
  const webview = document.querySelector('webview');
  Console.log('[browser.js: event] navigateStart start.');
  Console.log(event);
}

// function handleUpdateURL(event) {
//   Console.log('[browser.js: event] handleUpdateURL.');
//   Console.log(event);
// }

function handleLoadStop(event) {
  Console.log('[browser.js: event] load stop.');
  // We don't remove the loading class immediately, instead we let the animation
  // finish, so that the spinner doesn't jerkily reset back to the 0 position.
  isLoading = false;
}

function handleLoadAbort(event) {
  Console.log('[browser.js: event] load abort.');
  Console.log(`  url: ${event.url}`);
  Console.log(`  isTopLevel: ${event.isTopLevel}`);
  Console.log(`  type: ${event.type}`);
}

function handleLoadRedirect(event) {
  Console.log('[browser.js: event] load redirect.');
  Console.log(event);
  resetExitedState();
  // document.querySelector('#location').value = event.newUrl;
}

function getNextPresetZoom(zoomFactor) {
  const preset = [
    0.25,
    0.33,
    0.5,
    0.67,
    0.75,
    0.9,
    1,
    1.1,
    1.25,
    1.5,
    1.75,
    2,
    2.5,
    3,
    4,
    5,
  ];
  let low = 0;
  let high = preset.length - 1;
  let mid;
  while (high - low > 1) {
    mid = Math.floor((high + low) / 2);
    if (preset[mid] < zoomFactor) {
      low = mid;
    } else if (preset[mid] > zoomFactor) {
      high = mid;
    } else {
      return {
        low: preset[mid - 1],
        high: preset[mid + 1],
      };
    }
  }
  return { low: preset[low], high: preset[high] };
}

function increaseZoom() {
  const webview = document.querySelector('webview');
  webview.getZoom((zoomFactor) => {
    const nextHigherZoom = getNextPresetZoom(zoomFactor).high;
    webview.setZoom(nextHigherZoom);
    document.forms['zoom-form']['zoom-text'].value = nextHigherZoom.toString();
  });
}

function decreaseZoom() {
  const webview = document.querySelector('webview');
  webview.getZoom((zoomFactor) => {
    const nextLowerZoom = getNextPresetZoom(zoomFactor).low;
    webview.setZoom(nextLowerZoom);
    document.forms['zoom-form']['zoom-text'].value = nextLowerZoom.toString();
  });
}

function openZoomBox() {
  document.querySelector('webview').getZoom((zoomFactor) => {
    const zoomText = document.forms['zoom-form']['zoom-text'];
    zoomText.value = Number(zoomFactor.toFixed(6)).toString();
    document.querySelector('#zoom-box').style.display = '-webkit-flex';
    zoomText.select();
  });
}

function closeZoomBox() {
  document.querySelector('#zoom-box').style.display = 'none';
}

function openFindBox() {
  document.querySelector('#find-box').style.display = 'block';
  document.forms['find-form']['find-text'].select();
}

function closeFindBox() {
  const findBox = document.querySelector('#find-box');
  findBox.style.display = 'none';
  findBox.style.left = '';
  findBox.style.opacity = '';
  document.querySelector('#find-results').innerText = '';
}

function closeBoxes() {
  closeZoomBox();
  closeFindBox();
}
