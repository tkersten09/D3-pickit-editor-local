onload = () => {
  const webview = document.querySelector('webview');
  const indicator = document.querySelector('.indicator');
  console.log(webview);
};

const { ipcRenderer } = require('electron');

console.log('[init.html] hey');
document.addEventListener('DOMContentLoaded', () => {
  console.log('[init.html: event] DOMContentLoaded');
});

document.addEventListener('load', () => {
  console.log('[init.html: event] load');
});

function strMapToObj(strMap) {
  const obj = Object.create(null);
  for (const [k, v] of strMap) {
    obj[k] = v;
  }
  return obj;
}
function strMapToJson(strMap) {
  return JSON.stringify(strMapToObj(strMap));
}

function navigateTo(className) {
  console.log('[init.html: event] navigateTo');
  ipcRenderer.sendTo(1, 'navigateTo', className);
}

document.addEventListener('DOMContentLoaded', () => {
  console.log('[init.html: event] DOMContentLoaded buildnumberCheckboxes');
  let buildnumberCheckboxes = document.querySelectorAll('input[buildnumber]');
  buildnumberCheckboxes.forEach((currentValue) => {
    console.log('add change event');
    currentValue.addEventListener('change', () => {
      let newSelection = new Map();
      let checked = false;
      let buildnumber;
      buildnumberCheckboxes = document.querySelectorAll('input[buildnumber]');
      console.log('run change event');
      buildnumberCheckboxes.forEach((cValue) => {
        checked = false;
        buildnumber = cValue.getAttribute('buildnumber');
        if (cValue.checked) {
          checked = true;
        }
        newSelection = newSelection.set(buildnumber, checked);
      });
      console.log(`newSelection: ${newSelection}`);
      const newSelectionJson = strMapToJson(newSelection);
      ipcRenderer.sendTo(1, 'newSelection', className, newSelectionJson);
    });
  });
});
