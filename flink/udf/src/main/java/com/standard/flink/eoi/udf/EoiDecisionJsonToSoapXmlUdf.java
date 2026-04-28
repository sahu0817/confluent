package com.standard.flink.eoi.udf;

import com.standard.flink.eoi.soap.EoiDecisionToSoapXml;
import org.apache.flink.table.annotation.DataTypeHint;
import org.apache.flink.table.annotation.FunctionHint;
import org.apache.flink.table.functions.ScalarFunction;

/**
 * Flink SQL scalar function: JSON decision payload → Workday SOAP XML string.
 *
 * <p>Register in Java Table API:
 *
 * <pre>{@code
 * tEnv.createTemporarySystemFunction(
 *     "EOI_JSON_TO_SOAP",
 *     EoiDecisionJsonToSoapXmlUdf.class);
 * // SELECT EOI_JSON_TO_SOAP(decision_json) FROM ...
 * }</pre>
 *
 * <p>SQL DDL (JAR must be on classpath / UDF JAR):
 *
 * <pre>{@code
 * CREATE FUNCTION eoi_json_to_soap AS
 *   'com.standard.flink.eoi.udf.EoiDecisionJsonToSoapXmlUdf' LANGUAGE JAVA;
 * }</pre>
 */
public class EoiDecisionJsonToSoapXmlUdf extends ScalarFunction {

    private static final long serialVersionUID = 1L;

    @FunctionHint(output = @DataTypeHint("STRING"))
    public String eval(String decisionJson) {
        if (decisionJson == null) {
            return null;
        }
        try {
            return EoiDecisionToSoapXml.jsonToSoapXml(decisionJson);
        } catch (Exception e) {
            throw new RuntimeException("EOI JSON → SOAP conversion failed", e);
        }
    }

    /**
     * @param bsvcApiVersion Workday web service version on the request element (e.g. {@code v42.0}).
     */
    @FunctionHint(output = @DataTypeHint("STRING"))
    public String eval(String decisionJson, String bsvcApiVersion) {
        if (decisionJson == null) {
            return null;
        }
        try {
            return EoiDecisionToSoapXml.jsonToSoapXml(decisionJson, bsvcApiVersion);
        } catch (Exception e) {
            throw new RuntimeException("EOI JSON → SOAP conversion failed", e);
        }
    }
}
