package com.standard.flink.eoi.soap;

import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

class EoiDecisionToSoapXmlTest {

    @Test
    void sampleJsonProducesExpectedSoapShape() throws Exception {
        Path base = Path.of(System.getProperty("user.dir"));
        Path json = base.getParent().resolve("eoi_decision_sample.json");
        if (!Files.isRegularFile(json)) {
            json = base.resolve("..").resolve("eoi_decision_sample.json").normalize();
        }
        String in = Files.isRegularFile(json)
                ? Files.readString(json)
                : "{\n"
                        + "  \"worker_id\": \"11111111\",\n"
                        + "  \"worker_id_type\": \"Employee_ID\",\n"
                        + "  \"worker_descriptor\": null,\n"
                        + "  \"benefit_plan_id\": \"EMPLOYER_SPECIFIC_PLAN_CODE_VALUE\",\n"
                        + "  \"benefit_plan_id_type\": \"Benefit_Plan_ID\",\n"
                        + "  \"benefit_plan_descriptor\": null,\n"
                        + "  \"approve_for_selected\": false,\n"
                        + "  \"deny_for_selected\": true,\n"
                        + "  \"eoi_decision_date\": \"2023-10-27\"\n"
                        + "}";

        String xml = EoiDecisionToSoapXml.jsonToSoapXml(in);

        assertTrue(xml.contains("Put_Evidence_of_Insurability_Request"));
        assertTrue(xml.contains("urn:com.workday/bsvc"));
        assertTrue(xml.contains("11111111"));
        assertTrue(xml.contains("Employee_ID"));
        assertTrue(xml.contains("EMPLOYER_SPECIFIC_PLAN_CODE_VALUE"));
        assertTrue(xml.contains("Benefit_Plan_ID"));
        assertTrue(xml.contains("<bsvc:Approve_for_selected>false</bsvc:Approve_for_selected>"));
        assertTrue(xml.contains("<bsvc:Deny_for_selected>true</bsvc:Deny_for_selected>"));
        assertTrue(xml.contains("<bsvc:EOI_Approve_Or_Deny_Date>2023-10-27</bsvc:EOI_Approve_Or_Deny_Date>"));
        assertTrue(xml.contains("bsvc:version=\"v42.0\""));
    }
}
