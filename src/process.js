var fs = require('fs')
//var PNG = require('pngjs').PNG
var jpeg = require('jpeg-js')
var convnetjs = require('convnetjs')
var directory = process.argv[2]

const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const { document } = (new JSDOM(``)).window;
var images = []
var layer_defs = []
layer_defs.push({type:'input', out_sx:32, out_sy:24, out_depth:1});
layer_defs.push({type:'conv', sx:5, filters:16, stride:1, pad:2,activation:'relu'})
layer_defs.push({type:'pool', sx:2, stride:2})
layer_defs.push({type:'conv', sx:5, filters:20, stride:1,pad:2, activation:'relu'})
layer_defs.push({type:'pool', sx:2, stride:2})
layer_defs.push({type:'conv', sx:5, filters:20, stride:1,pad:2, activation:'relu'})
layer_defs.push({type:'pool', sx:2, stride:2})
layer_defs.push({type:'softmax', num_classes:3})

var net = new convnetjs.Net();
net.makeLayers(layer_defs);
var trainer = new convnetjs.Trainer(net, {method: 'adadelta', l2_decay: 0.001,
                                    batch_size: 1});


fs.readdir(__dirname+'/artificial',function(err,items){

  if(err) {
    console.log(err);
    return;
  }
  for(var y=0;y<20;y++) {
    for (var indices=[],i=0;i<items.length;++i) indices[i]=i;
    indices = shuffle(indices)
    for(var x =items.length-1;x>=0;x--){

        var index = indices[x]
        var direction = items[index].split('-')[0]
        var dint;
        //console.log(direction)
        if(direction ==="left") {
          dint = 0
        }
        else if(direction==='straight') {
          dint = 1
        }
        else if(direction === 'right') {
          dint = 2
        }
        else {
          continue
        }
        var jpegData = fs.readFileSync(__dirname+'/artificial/'+items[index])
        var rawImageData = jpeg.decode(jpegData,true)
        var mat = []
        //console.log(rawImageData.data[0])
        for(var i =0;i<24;i++) {
          //mat.push([])
          for(var j=0;j<32;j++) {
            var row = i*51200
            //mat[i].push([])
            mat.push((rawImageData.data[row+j*80]+rawImageData.data[row+j*81]+rawImageData.data[row+j*82])/765)
          }
        }
        //console.log(mat)
        var vol = new convnetjs.Vol(32,24,1)

        vol.w = mat
        var stats = trainer.train(vol,dint)
      //  console.log(stats.loss)

    }
  }
  //var filename = __dirname+'/Trial-4-Labeled/left-52.jpg';
  fs.readdir(__dirname+'/Trial-4-Labeled',function(err,items){
    for(var x =0;x<items.length;x++) {
      var jpegData = fs.readFileSync(__dirname+'/Trial-4-Labeled/'+items[x])
      var rawImageData = jpeg.decode(jpegData,true)
      var mat = []
      //console.log(rawImageData.data[0])
      for(var i =0;i<24;i++) {
        //mat.push([])
        for(var j=0;j<32;j++) {
          var row = i*51200
          //mat[i].push([])
          mat.push((rawImageData.data[row+j*80]+rawImageData.data[row+j*81]+rawImageData.data[row+j*82])/765)
        }
      }
      //console.log(mat)
      var vol = new convnetjs.Vol(32,24,1)
      //console.log(x)
      vol.w = mat
      var prob = net.forward(vol)
      console.log(prob.w+' '+items[x])
    }
  })

  //var json = net.toJSON()
  //var str = JSON.stringify(json);
//  console.log('net is'+str)

})

// http://stackoverflow.com/questions/962802#962890
function shuffle(array) {
  var tmp, current, top = array.length;
  if(top) while(--top) {
    current = Math.floor(Math.random() * (top + 1));
    tmp = array[current];
    array[current] = array[top];
    array[top] = tmp;
  }
  return array;
}

//https://stackoverflow.com/questions/5836833/create-a-array-with-random-values-in-javascript
