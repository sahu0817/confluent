package com.standard.flink.eoi.cli;

import com.standard.flink.eoi.soap.EoiDecisionToSoapXml;
import java.nio.file.Files;
import java.nio.file.Path;

/** Prints SOAP XML for a JSON file (no Flink). */
public final class EoiDecisionToSoapCli {

    public static void main(String[] args) throws Exception {
        Path jsonPath =
                args.length > 0
                        ? Path.of(args[0])
                        : Path.of(System.getProperty("user.dir"))
                                .resolve("../eoi_decision_sample.json")
                                .normalize();
        if (!Files.isRegularFile(jsonPath)) {
            System.err.println("JSON file not found: " + jsonPath.toAbsolutePath());
            System.err.println("Usage: java ... EoiDecisionToSoapCli [<path-to-decision.json>]");
            System.exit(1);
        }
        String json = Files.readString(jsonPath);
        System.out.println(EoiDecisionToSoapXml.jsonToSoapXml(json));
    }
}
