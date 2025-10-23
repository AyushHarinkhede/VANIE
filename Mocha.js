var a=134;
console.log(a.toString());                 //134
console.log((245).toString()) ;            //245
console.log((123).toString()+10);          //12310
console.log((180 + 25).toString());        //125

//.tostring() are used the radix values like binary,octal,decimal,hexadeccimal combinationn of this can give the final value.
var b=333;
console.log(b.toString(4));
console.log(b.toString(2));

//.toExponential method after decimal if the value is low ,they  add zero instead any number.
var c=2.11;
console.log(c.toExponential());  //2.11e+0
console.log(c.toExponential(1)); //2.1e+0
console.log(c.toExponential(3)); //2.110e+0
console.log(c.toExponential(5)); //2.11000e+0

//.tofixed method used for set the exact value after the decimal if there is no numb. then it again enter zera there.
var d=8.6569;
console.log(d.toFixed(4));  //8.6569
console.log(d.toFixed(1));  //8.7
console.log(d.toFixed(3));  //8.657
console.log(d.toFixed(2));  //8.66

//.toPecision() method print the value by cut 1 no. means input is 1234(3) then output will be 123.
var e=5.21011;
console.log(e.toPrecision(3));  //0.210
console.log(e.toPrecision(2));  //0.21
console.log(e.toPrecision(4));  //0.2101
console.log(e.toPrecision(5));  //0.21011

//.valueof() method returns the values from numbers to number
var f=729;
console.log(f.valueOf());        //729
console.log((152).valueOf());    //152
console.log((7493+83).valueOf());//7576
console.log((4251-23).valueOf());//4228

//global methods of numbers
Number(true);        //1
Number(false);       //0
Number("05");        //05
Number("  05");      //05
Number("05  ");      //05
Number("45.05");     //45.05
Number("45,09");     
Number("78 89");
Number("Vaidehi");

//Number.isfinite() method gives output always true till the value is infinite. Finite value =true; Infinite value=false;.
 var g=Number.isFinite(123);

 //Number.isinteger method gives output true and false wheather is not an integer then true otherwise false.
 Number.isInteger(10);
 Number.isInteger(10.5);//Number method :String ko number mein convert krke add krke output.
var a="88";

 var num=Number(a);
 console.log(num+10);