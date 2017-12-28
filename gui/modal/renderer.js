const eless = require('electron-less');

eless({
  paths: ['./gui/modal/city-lights-ui-atom/', 'gui/modal/city-lights-ui-atom/'],
  // options.source is required
  source: 'gui/modal/city-lights-ui-atom/index-new.less',
  // options.id is optional.
  // options.id defaults to hasha(source)
  id: 'myStyles',
  // options.variables is optional
  // options.variables gets turned into less variables
  // that get prefixed to the options.source file text
  // variables: {
  // }
}).then(() => {
  console.log('Styles appended to head element');
});

eless({
  paths: [],
  // options.source is required
  source: 'gui/modal/styles.less',
  // options.id is optional.
  // options.id defaults to hasha(source)
  id: 'myStyles2',
  // options.variables is optional
  // options.variables gets turned into less variables
  // that get prefixed to the options.source file text,
}).then(() => {
  console.log('Styles appended to head element');
});
