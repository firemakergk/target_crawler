var page = require('webpage').create(),
system = require('system'),
t,
address;
if (system.args.length != 3) {
    console.log('Usage: loadspeed.js <some URL> <some xpath>');
    phantom.exit();
}

address = system.args[1];

page.open(address,
function(status) {
    var xpath = system.args[2];
    
    if (status !== 'success') {
        console.log('FAIL to load the address');
    } else {
        var res = page.evaluate(function(xpath) {
            var aList = document.evaluate(
                xpath+'//a',
                document,
                null,
                XPathResult.ORDERED_NODE_ITERATOR_TYPE,
                null);
            var aStr = '{\"isSuccess\":true,\"itemList\":[';
            while((a = aList.iterateNext())!=null){
                if(a.innerText !== null && a.innerText !== undefined && a.innerText !== ''){
                    aStr += '{\"text\":\"'+a.innerText+'\",\"href\":\"'+a.href+'\"},'
                }
            }
              aStr = aStr.substring(0,aStr.length-1);
              aStr += ']}'
            return aStr;
            },xpath);
        console.log(res);
    }
    phantom.exit();
});