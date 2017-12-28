const zerorpc = require("zerorpc")
let client = new zerorpc.Client()

client.connect("tcp://127.0.0.1:4242")

client.invoke("echo", "server ready", (error, res) => {
  if(error || res !== 'server ready') {
    console.error("echo: " + error)
  } else {
    console.log("server is ready")
  }
})

new_selection = new Map()
new_selection.set('text1', 'input1')
new_selection.set('text2', 'input2')
var fruits = [];
fruits.push('banana', 'apple', 'peach');
fruits_json = JSON.stringify(fruits)

function objToStrMap(obj) {
    let strMap = new Map();
    for (let k of Object.keys(obj)) {
        strMap.set(k, obj[k]);
    }
    return strMap;
}

function strMapToObj(strMap) {
    let obj = Object.create(null);
    for (let [k,v] of strMap) {
        // We don’t escape the key '__proto__'
        // which can cause problems on older engines
        obj[k] = v;
    }
    return obj;
}
function strMapToJson(strMap) {
    return JSON.stringify(strMapToObj(strMap));
}

client.invoke("init", (error, res) => {
  if(error) {
    console.error(error)
  } else {
    console.log("init() res:" + res)
  }
})

// webview.addEventListener('ipc-message', (event) => {
//   console.log(event.channel)
//   // Prints "pong"
// })
// 
console.log(strMapToJson(new_selection))
client.invoke("update", "crusaider", strMapToJson(new_selection), (error, res) => {
  if(error) {
    console.error(error)
  } else {
    console.log("invoke res:" + res)
  }
})
