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

//var net = new convnetjs.Net();
//net.makeLayers(layer_defs);


//change file path
//0.0001 and 3 is best for artificial
var decays = [0.005,0.004,0.006]
var batch_sizes = [3,2,4]
var best_val
var best_net
fs.readdir(__dirname+'/Trial-4-Labeled-processed/',function(err,items){
//  console.log(items.length)
  if(err) {
    console.log(err);
    return;
  }
  var bestScore = 0
  var bestDecay
  var bestBatch
  var bestNet
  decays.forEach(function(d){
    batch_sizes.forEach(function(b) {

      var validation_set_size = parseInt(items.length/5)

      for (var indices=[],i=0;i<items.length;++i) indices[i]=i;
      indices = shuffle(indices)
      var validation_set=[]
      var training_set=[]
      var score =0
      var net
      var val_len=0
      for(var iter = 0;iter<1;iter++){
        net = new convnetjs.Net();
        net.makeLayers(layer_defs);
        var trainer = new convnetjs.Trainer(net, {method: 'adadelta', l2_decay: d,
                                            batch_size: b});
        var lowerBound = iter*validation_set_size
        var upperBound
        if(iter!==4){
          upperBound = lowerBound+validation_set_size
        }
        else {
          upperBound = items.length
        }
        validation_set = []
        training_set = []
        for(var ind=0;ind<items.length;ind++){
          if(ind>=lowerBound&&ind<upperBound){
            validation_set.push(items[indices[ind]])
          }
          else{
            training_set.push(items[indices[ind]])
          }
        }
        //change predict back to original version
        for(var x =0;x<training_set.length;x++){

            //var index = indices[x]
            //var direction = items[index].split('-')[0]
            var direction = training_set[x].split('-')[0]
            var dint;
            //console.log(direction)
            if(direction[0] ==='l') {
              dint = 0
            }
            else if(direction[0]==='s') {
              dint = 1
            }
            else if(direction[0] === 'r') {
              dint = 2
            }
            else {
              continue
            }
            //change file path
            var jpegData = fs.readFileSync(__dirname+'/Trial-4-Labeled-processed/'+training_set[x])
            var rawImageData = jpeg.decode(jpegData,true)
            //console.log('rawImage\n')
            // console.log(rawImageData);
            // console.log(training_set[x])
            var mat = []
            //console.log(rawImageData.data[0])
            // for(var i =0;i<24;i++) {
            //   //mat.push([])
            //   for(var j=0;j<32;j++) {
            //     var row = i*51200
            //     //mat[i].push([])
            //     mat.push((rawImageData.data[row+j*80]+rawImageData.data[row+j*81]+rawImageData.data[row+j*82])/765)
            //   }
            // }
            for(var i =0;i<24;i++) {
              //mat.push([])
              for(var j=0;j<32;j++) {
                //var row = i*51200
                //mat[i].push([])
                mat.push(rawImageData.data[i*32*4+j*4])
              }
            }

            //console.log('training mat='+mat)
            //console.log('\n\n\n')
            //NOTE: show if this mat is really the same as image before
            //console.log(mat)
            var vol = new convnetjs.Vol(32,24,1)

            vol.w = mat
            var stats = trainer.train(vol,dint)
          // console.log('x='+x)
           //console.log(stats.loss)

        }
        val_len+=validation_set.length
        score += predict(net,validation_set,'Trial-4-Labeled-processed')
        console.log('score='+score)
        console.log('validation.length='+validation_set.length);
        console.log('d= '+d)
        console.log('b= '+b)
      }

      if(score>bestScore) {
        bestDecay = d
        bestBatch = b
        bestNet = net
        bestScore = score
      }
    })
  })
  console.log('bestdecay= '+bestDecay)
  console.log('bestbatch= '+bestBatch)
  console.log('bestscore= '+bestScore)
  var len = items.length
  console.log('total files= '+len)
  var files = fs.readdir(__dirname+'/test-set',function(err,items){
      var s = predict(bestNet,items,'test-set')
      console.log('predicted_score='+s)
      console.log('filesize='+items.length)
  })


})

//filenames:string array is an array of filenames.
//lowerBound is inclusive, upperbound is exclusive
function predict(net,filenames,dir) {
  var predicted_score=0
  //fs.readdir(__dirname+'/'+dir,function(err,items){
    for(var x =0;x<filenames.length;x++) {
      var jpegData = fs.readFileSync(__dirname+'/'+dir+'/'+filenames[x])
      var rawImageData = jpeg.decode(jpegData,true)
      var mat = []
      //console.log(rawImageData.data[0])
      //var index = indices[x]
      var direction = filenames[x].split('-')[0]
      var dint;
      //console.log(direction)
      if(direction[0] ==='l') {
        dint = 0
      }
      else if(direction[0]==='s') {
        dint = 1
      }
      else if(direction[0] === 'r') {
        dint = 2
      }
      else {
        continue
      }
      // for(var i =0;i<24;i++) {
      //   mat.push([])
      //   for(var j=0;j<32;j++) {
      //     //var row = i*51200
      //     //mat[i].push([])
      //     mat[i].push(rawImageData.data[i*32*4+j*4])
      //   }
      // }
      for(var i =0;i<24;i++) {
        //mat.push([])
        for(var j=0;j<32;j++) {
          //var row = i*51200
          //mat[i].push([])
          mat.push(rawImageData.data[i*32*4+j*4])
        }
      }
      //console.log('predict='+mat)
      //console.log('\n\n\n')
      var vol = new convnetjs.Vol(32,24,1)
      //console.log(x)
      vol.w = mat
      var prob = net.forward(vol)
      //console.log(prob.w+' '+filenames[x])
      if(prob.w[dint]>=prob.w[0]&&prob.w[dint]>=prob.w[1]&&prob.w[dint]>=prob.w[2]){
        //console.log(prob.w+' '+filenames[x])
        predicted_score++
      }
      else{
        console.log(prob.w+' '+filenames[x])
        //console.log(filenames[x])
      }
    }
    return predicted_score
  //})
}

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
