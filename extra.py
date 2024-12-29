import sc3nb as scn
sc = scn.startup(start_server=False)
sc.lang.cmds(
    r"""
        "sc3nb - Registering OSC /return callback".postln;
        // NetAddr.useDoubles = true;
        r = r ? ();
        r.callback = { arg code, ip, port;
            var result = code.interpret;
            var addr = NetAddr.new(ip, port);
            var prependSize = { arg elem;
                if (elem.class == Array){
                    elem = [elem.size] ++ elem.collect(prependSize);
                }{
                    elem;
                };
            };
            var msgContent = prependSize.value(result);
            addr.sendMsg(^replyAddress, msgContent);
            result;  // result should be returned
        };""",
    pyvars={"replyAddress": "/return"},
)
sc.start_server()