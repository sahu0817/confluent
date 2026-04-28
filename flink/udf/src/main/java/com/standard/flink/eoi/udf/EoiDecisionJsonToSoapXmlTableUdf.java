package com.standard.flink.eoi.udf;

import com.standard.flink.eoi.soap.EoiDecisionToSoapXml;
import org.apache.flink.table.annotation.DataTypeHint;
import org.apache.flink.table.annotation.FunctionHint;
import org.apache.flink.table.functions.TableFunction;
import org.apache.flink.types.Row;

/**
 * Table function variant: emits a single row with the SOAP XML (and optional error column pattern).
 *
 * <p>Use when you prefer {@code CROSS JOIN LATERAL TABLE(udf(col))} or need row expansion.
 */
public class EoiDecisionJsonToSoapXmlTableUdf extends TableFunction<Row> {

    private static final long serialVersionUID = 1L;

    @FunctionHint(output = @DataTypeHint("ROW<soap_xml STRING>"))
    public void eval(String decisionJson) {
        if (decisionJson == null) {
            return;
        }
        try {
            collect(Row.of(EoiDecisionToSoapXml.jsonToSoapXml(decisionJson)));
        } catch (Exception e) {
            throw new RuntimeException("EOI JSON → SOAP conversion failed", e);
        }
    }

    @FunctionHint(output = @DataTypeHint("ROW<soap_xml STRING>"))
    public void eval(String decisionJson, String bsvcApiVersion) {
        if (decisionJson == null) {
            return;
        }
        try {
            collect(Row.of(EoiDecisionToSoapXml.jsonToSoapXml(decisionJson, bsvcApiVersion)));
        } catch (Exception e) {
            throw new RuntimeException("EOI JSON → SOAP conversion failed", e);
        }
    }
}
