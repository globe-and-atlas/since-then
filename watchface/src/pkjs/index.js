// Since Then, phone side: the settings page only. The watch holds all of its data.
var Clay = require('@rebble/clay');
var config = require('./config.json');

new Clay(config); // sends Setting_Lens to the watch when the page closes
