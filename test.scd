1.postln;
"Hello MUS 499C".postln;
3+5.postln;

"Evan M".postln;

(
var a = 1 + 15;
a.postln;
)

(
x = {
    var sig, freq, freq2, width;
    freq = LFSaw.ar(freq: 1/5, iphase: 1).exprange(200, 1500);
    freq2 = LFNoise0.ar(freq: 40 ! 2).range(1, 100);
    freq = (freq + freq2).round(50);
    width = LFTri.ar(freq: 0.2).exprange(0.02, 0.5);
    sig = VarSaw.ar(freq: freq, iphase: 0, width: width, mul: 0.05);
    sig = sig ! 2;
}.play;
)
\\ hello!
x.free;


