// HW2

// First, save this scd file as a new file, renaming it with your Last name at the beginning of the file name (e.g. "Fieldsteel HW2.scd"). Write your answers and upload this renamed file to the course website for your submission.

// ----------
// Problem 1.
// The following UGen function produces an error when we attempt to play it. Study the code and the error message, then correct the error and add a comment indicating what the problem was.

s.boot;

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

x.free;

// PROBLEM: variable "freq2" wasn't defined.
// Side note: there was a mismatch in sample rate between my microphone and SC_AudioDriver. oops :)

// ----------
// Problem 2.
// The following UGen function produces an error when we attempt to play it. Study the code and the error message, then correct the error and add a comment indicating what the problem was.

(
x = {
	var sig, freq, amp;
	freq = LFNoise0.ar(freq: 9).exprange(40, 500);
	amp = LFSaw.ar(freq: 9, iphase: 1).range(0, 1).sqrt.neg + 1;
	sig = SinOsc.ar(freq: freq, mul: 0.2) * amp;
	sig = sig ! 2;
}.play;
)

x.free;

// PROBLEM: comma used between LFSaw.ar() and range(), instead of a period.

// ----------
// Problem 3.
// The following code does not produce an error, but fails to produce sound. Correct the error and add a comment indicating what the problem was.

(
x = {
	var sig, noiseHz;
	noiseHz = LFNoise1.ar(freq: 10).exprange(500, 5000);
	sig = LFDNoise1.ar(freq: noiseHz, mul: 0.08);
	//sig = sig * 0;
	sig = sig ! 2;
}.play;
)

x.free;

// PROBLEM: the line "sig = sig * 0;" essentially mutes the UGen (amplitude multiplication by 0)

// ----------
// Problem 4.
// The following code does not produce an error, but fails to produce sound. Correct the error and add a comment indicating what the problem was.

(
x = {
	var sig, mod;
	mod = SinOsc.kr(freq: 1/4, phase: 3pi/2).range(0.02, 1);
	sig = PinkNoise.ar(0.2 ! 2);
	sig = sig * mod;
	sig = sig ! 2;
}.play;
)

x.free;

// PROBLEM: PinkNoise was missing class method ".ar()" in order to sound.

// ----------
// Problem 5.
// Create and play a UGen function that emulates a police siren. You can use this video for reference:

// https://www.youtube.com/watch?v=1G9mNBUymP8

// You'll have to use your ears to figure out the right numbers. Using a periodic signal generator as a frequency modulator provides a rough solution, but using a looping envelope generator (e.g. Env.circle) allows more precision. It doesn't have to be identical to the sound in the video, but try to get as close as you can.

(
x = {
	var sig, env;
	env = EnvGen.kr(
		envelope: Env.adsr(
			attackTime: 1.5,
			decayTime: 2,
			sustainLevel: 650/1300,
			releaseTime: 2,
			peakLevel: 1.0,
			curve: -1.0,
			bias: 0.0

		).circle,
		doneAction: 2
	);
	sig = SinOsc.ar(1230 * env);
	sig = sig * 0.05 ! 2;
}.play;
)

x.release(2);


// ----------
// Problem 6.
// Copy, paste, and modify the code from the previous example in the following way: Add an argument that controls the rate at which the siren's pitch fluctuates, and add an amplitude envelope that allows the sound to be faded out gradually. In addition to code that plays the siren function, add at least one line of code that sets this parameter to a new value (running this line should make the siren pitch fluctuate faster or slower), and another line of code that slowly fades out the sound (as if the police car is driving away into the distance).

(
~siren = {
	|rate = 1.0| // adjust rate
	var sig, env, env2;
	env = EnvGen.kr(
		envelope: Env.adsr(
			attackTime: 1.5 / rate,
			decayTime: 2 / rate,
			sustainLevel: 650 / 1300,
			releaseTime: 2 / rate,
			peakLevel: 1.0,
			curve: -1.0,
			bias: 0.0
		).circle
	);
	env2 = EnvGen.kr(
		envelope: Env.adsr(
			attackTime: 1.0,
			decayTime: 2,
			releaseTime: 4
		),
		gate: \fade.kr(1),
		doneAction: 2
	);
	sig = SinOsc.ar(1230 * env);
	sig = sig * 0.1 * env2 ! 2;
}.play;
)

~siren.set(\rate, 5.0); // adjust rate
~siren.set(\fade, 0); // fade out gradually


// ----------
// Problem 7.
// If you grew up with a landline phone in your house, or if you've watched classic horror movies, you may have heard the sound of a telephone that's been left off the hook for too long. It's kind of a disturbing sound: a periodic on-off pulsation of a harsh, mid-range tone. If you have no idea what I'm talking about, paste this link into your browser:

// https://www.youtube.com/watch?v=KO_YErq1M-M

// Create and play a UGen function that emulates this sound. From a spectral analysis perspective, I will tell you that it contains the following sinusoidal frequencies: [1400, 2060, 2450, 2600] Hz. The rest is up to you!

(
x = {
	var sig, env;
	env = EnvGen.ar(
		envelope: Env.cutoff(
			releaseTime:2,
			level: 1.0,
			curve: 'lin'
		).circle,
		doneAction: 2
	);
	sig = Blip.ar([1400, 2060, 2450, 2600], numharm: 0, mul: 0.05)
	* EnvGen.kr(Env.perc(0.07, 0.13, level: 1, curve: -10000.0).circle);
	sig = sig ! 2;
}.play;
)

x.release(2);

// NOTES:
// 1. 300 BPM = 5 beats per second, (the off-hook beep rate).
// 2. I listened to other off-hook phone samples that didn't have periodic "clicking," so I took this to be an issue with the video's audio and didn't include it.

// ----------
// Problem 8.
// Copy, paste, and modify the code from the previous example so that the phone pulses now alternate between "normal" and one octave higher. The simplest way to do this is to incorporate a new UGen that operates as a frequecy multiplier, whose output values alternate between 1 and 2 at an appropriate rate.

(
x = {
	|alternate = 0.2| // adjust octave alternating, (0.1=original, 0.2=every other, [0.4, 0.9]= floor(x/2) original, ceil(x/2) 8va).
	var sig, env;
	env = EnvGen.ar(
		envelope: Env.cutoff(
			releaseTime:2,
			level: 1.0,
			curve: 'lin'
		).circle,
		doneAction: 2
	);
	sig = Blip.ar([1400, 2060, 2450, 2600] * Select.kr(PulseCount.kr(Impulse.kr(1 / alternate)) % 2, [2, 1]), numharm: 0, mul: 0.05)
	* EnvGen.kr(Env.perc(0.07, 0.13, level: 2, curve: -1000.0).circle);
	sig = sig ! 2;
}.play;
)

x.release(2);

// NOTES:
// Impulse.kr(1/dur) sends an impulse every dur seconds
// PulseCount.kr(trig, reset) counts how many times its argument occurs. We want every other beat changed, so we take its return value mod 2.
// Select.kr(which, array) maps elements of "which" to "array". In this case, we map [0, 1] to [1, 2] to shift every other beat up an octave.
// There's probably a much easier way of doing this...


