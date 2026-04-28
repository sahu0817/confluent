package com.standard.flink.eoi.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Mirrors {@code eoi_decision_sample.json} (Workday EOI decision payload).
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class EoiDecision {

    @JsonProperty("worker_id")
    private String workerId;

    @JsonProperty("worker_id_type")
    private String workerIdType;

    @JsonProperty("worker_descriptor")
    private String workerDescriptor;

    @JsonProperty("benefit_plan_id")
    private String benefitPlanId;

    @JsonProperty("benefit_plan_id_type")
    private String benefitPlanIdType;

    @JsonProperty("benefit_plan_descriptor")
    private String benefitPlanDescriptor;

    @JsonProperty("approve_for_selected")
    private Boolean approveForSelected;

    @JsonProperty("deny_for_selected")
    private Boolean denyForSelected;

    @JsonProperty("eoi_decision_date")
    private String eoiDecisionDate;

    public String getWorkerId() {
        return workerId;
    }

    public void setWorkerId(String workerId) {
        this.workerId = workerId;
    }

    public String getWorkerIdType() {
        return workerIdType;
    }

    public void setWorkerIdType(String workerIdType) {
        this.workerIdType = workerIdType;
    }

    public String getWorkerDescriptor() {
        return workerDescriptor;
    }

    public void setWorkerDescriptor(String workerDescriptor) {
        this.workerDescriptor = workerDescriptor;
    }

    public String getBenefitPlanId() {
        return benefitPlanId;
    }

    public void setBenefitPlanId(String benefitPlanId) {
        this.benefitPlanId = benefitPlanId;
    }

    public String getBenefitPlanIdType() {
        return benefitPlanIdType;
    }

    public void setBenefitPlanIdType(String benefitPlanIdType) {
        this.benefitPlanIdType = benefitPlanIdType;
    }

    public String getBenefitPlanDescriptor() {
        return benefitPlanDescriptor;
    }

    public void setBenefitPlanDescriptor(String benefitPlanDescriptor) {
        this.benefitPlanDescriptor = benefitPlanDescriptor;
    }

    public Boolean getApproveForSelected() {
        return approveForSelected;
    }

    public void setApproveForSelected(Boolean approveForSelected) {
        this.approveForSelected = approveForSelected;
    }

    public Boolean getDenyForSelected() {
        return denyForSelected;
    }

    public void setDenyForSelected(Boolean denyForSelected) {
        this.denyForSelected = denyForSelected;
    }

    public String getEoiDecisionDate() {
        return eoiDecisionDate;
    }

    public void setEoiDecisionDate(String eoiDecisionDate) {
        this.eoiDecisionDate = eoiDecisionDate;
    }
}
