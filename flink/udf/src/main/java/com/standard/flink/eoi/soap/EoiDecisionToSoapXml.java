package com.standard.flink.eoi.soap;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.standard.flink.eoi.model.EoiDecision;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.util.Objects;
import org.jdom2.Document;
import org.jdom2.Element;
import org.jdom2.Namespace;
import org.jdom2.output.Format;
import org.jdom2.output.XMLOutputter;

/**
 * Converts an {@link EoiDecision} (or JSON string) into a Workday
 * {@code Put_Evidence_of_Insurability_Request} SOAP envelope, matching the shape of
 * {@code eoi_request_sample.xml}.
 *
 * <p>Uses Jackson for JSON and JDOM2 for XML (namespaces, escaping, pretty print).
 */
public final class EoiDecisionToSoapXml {

    public static final String NS_SOAP = "http://schemas.xmlsoap.org/soap/envelope/";
    public static final String NS_BSVC = "urn:com.workday/bsvc";
    public static final String DEFAULT_BSVC_VERSION = "v42.0";
    public static final String DEFAULT_REFERENCE_DESCRIPTOR = "string";

    private static final Namespace SOAP = Namespace.getNamespace("soap", NS_SOAP);
    private static final Namespace BSVC = Namespace.getNamespace("bsvc", NS_BSVC);

    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    private EoiDecisionToSoapXml() {}

    public static EoiDecision parseJson(String json) throws Exception {
        Objects.requireNonNull(json, "json");
        return OBJECT_MAPPER.readValue(json.getBytes(StandardCharsets.UTF_8), EoiDecision.class);
    }

    public static String toSoapXml(EoiDecision decision) {
        return toSoapXml(decision, DEFAULT_BSVC_VERSION);
    }

    public static String toSoapXml(EoiDecision decision, String bsvcApiVersion) {
        Objects.requireNonNull(decision, "decision");
        String version = bsvcApiVersion != null && !bsvcApiVersion.isEmpty()
                ? bsvcApiVersion
                : DEFAULT_BSVC_VERSION;

        Element envelope = new Element("Envelope", SOAP);
        envelope.addNamespaceDeclaration(SOAP);
        envelope.addNamespaceDeclaration(BSVC);

        Element body = new Element("Body", SOAP);
        envelope.addContent(body);

        Element putReq = new Element("Put_Evidence_of_Insurability_Request", BSVC);
        putReq.setAttribute("version", version, BSVC);
        body.addContent(putReq);

        Element eoiData = new Element("Evidence_of_Insurability_Data", BSVC);
        putReq.addContent(eoiData);

        eoiData.addContent(workerReference(decision));
        eoiData.addContent(benefitPlanReference(decision));

        Element approve = new Element("Approve_for_selected", BSVC);
        approve.setText(booleanText(decision.getApproveForSelected()));
        eoiData.addContent(approve);

        Element deny = new Element("Deny_for_selected", BSVC);
        deny.setText(booleanText(decision.getDenyForSelected()));
        eoiData.addContent(deny);

        Element dateEl = new Element("EOI_Approve_Or_Deny_Date", BSVC);
        dateEl.setText(nullToEmpty(decision.getEoiDecisionDate()));
        eoiData.addContent(dateEl);

        Document doc = new Document(envelope);
        Format fmt = Format.getPrettyFormat();
        fmt.setEncoding("utf-8");
        fmt.setOmitDeclaration(false);
        fmt.setIndent("  ");
        XMLOutputter out = new XMLOutputter(fmt);
        StringWriter sw = new StringWriter();
        try {
            out.output(doc, sw);
        } catch (Exception e) {
            throw new IllegalStateException("Failed to serialize SOAP XML", e);
        }
        return sw.toString();
    }

    public static String jsonToSoapXml(String json) throws Exception {
        return toSoapXml(parseJson(json));
    }

    public static String jsonToSoapXml(String json, String bsvcApiVersion) throws Exception {
        return toSoapXml(parseJson(json), bsvcApiVersion);
    }

    private static Element workerReference(EoiDecision d) {
        Element ref = new Element("Worker_Reference", BSVC);
        ref.setAttribute(
                "Descriptor",
                d.getWorkerDescriptor() != null ? d.getWorkerDescriptor() : DEFAULT_REFERENCE_DESCRIPTOR,
                BSVC);
        Element id = new Element("ID", BSVC);
        id.setAttribute("type", nullToEmpty(d.getWorkerIdType()), BSVC);
        id.setText(nullToEmpty(d.getWorkerId()));
        ref.addContent(id);
        return ref;
    }

    private static Element benefitPlanReference(EoiDecision d) {
        Element ref = new Element("Benefit_Plan_Reference", BSVC);
        ref.setAttribute(
                "Descriptor",
                d.getBenefitPlanDescriptor() != null
                        ? d.getBenefitPlanDescriptor()
                        : DEFAULT_REFERENCE_DESCRIPTOR,
                BSVC);
        Element id = new Element("ID", BSVC);
        id.setAttribute("type", nullToEmpty(d.getBenefitPlanIdType()), BSVC);
        id.setText(nullToEmpty(d.getBenefitPlanId()));
        ref.addContent(id);
        return ref;
    }

    private static String booleanText(Boolean b) {
        return b != null ? Boolean.toString(b) : "false";
    }

    private static String nullToEmpty(String s) {
        return s != null ? s : "";
    }
}
