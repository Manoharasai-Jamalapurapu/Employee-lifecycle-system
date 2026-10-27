"""Streamlit dashboard for the synthetic employee lifecycle system."""
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
from engine.rules import detect_issues, evaluate_tasks
from validation.validate_data import validate

st.set_page_config(page_title="Employee Lifecycle Operations",page_icon="🧭",layout="wide")
st.title("Employee Lifecycle Operations")
st.caption("Synthetic-data demonstration: onboarding, access governance, assets, offboarding and auditability.")
data=Path("data")
if not (data/"employees.csv").exists():
    st.warning("Dataset not found. From the project root, run: `python -m generator.generate`")
    st.stop()
def read(name):
    f=data/f"{name}.csv"
    return pd.read_csv(f,keep_default_na=False) if f.exists() else pd.DataFrame()
employees=read("employees"); cases=read("onboarding_cases"); tasks=read("task_instances")
assets=read("assets"); access=read("access_requests"); audit=read("audit_events")
issues=detect_issues()
total=len(employees); active=int(employees["employment_status"].eq("Active").sum())
completed=int(tasks["status"].eq("Completed").sum()) if not tasks.empty else 0
pending=max(len(tasks)-completed,0)
sla=evaluate_tasks(tasks) if not tasks.empty else pd.DataFrame()
breaches=int(sla["sla_breach"].sum()) if not sla.empty else 0
active_risk=int(((access["provisioned"].astype(str).str.lower().isin(["true","1"])) & (~access["revoked"].astype(str).str.lower().isin(["true","1"]))).sum()) if not access.empty else 0
c1,c2,c3,c4,c5=st.columns(5)
c1.metric("Employees",f"{total:,}"); c2.metric("Active employees",f"{active:,}")
c3.metric("Tasks completed",f"{completed:,}",f"{completed/max(len(tasks),1):.1%}")
c4.metric("Overdue tasks",f"{breaches:,}"); c5.metric("Access not revoked",f"{active_risk:,}")
tab1,tab2,tab3,tab4=st.tabs(["Overview","Exceptions","Employees & tasks","Data quality"])
with tab1:
    l,r=st.columns(2)
    if not tasks.empty:
        status=tasks["status"].value_counts().rename_axis("status").reset_index(name="count")
        l.plotly_chart(px.bar(status,x="status",y="count",title="Task status distribution"),use_container_width=True)
    if not employees.empty:
        dept=employees["department_id"].value_counts().rename_axis("department_id").reset_index(name="employees")
        r.plotly_chart(px.bar(dept,x="department_id",y="employees",title="Employees by department"),use_container_width=True)
    st.subheader("Access requests by status")
    if not access.empty:
        st.plotly_chart(px.pie(access,names="request_status",title="Access request decisions"),use_container_width=True)
with tab2:
    st.write(f"Detected **{len(issues)}** possible issues using documented rules. Review before taking action.")
    if not issues.empty:
        severities=st.multiselect("Severity",sorted(issues["severity"].unique()),default=sorted(issues["severity"].unique()))
        types=st.multiselect("Issue type",sorted(issues["issue_type"].unique()),default=sorted(issues["issue_type"].unique()))
        st.dataframe(issues[issues["severity"].isin(severities)&issues["issue_type"].isin(types)],use_container_width=True,hide_index=True)
        st.download_button("Download exception report",issues.to_csv(index=False),"exception_report.csv","text/csv")
    else: st.success("No issues detected by the current rules.")
with tab3:
    q=st.text_input("Search employee ID, name or email")
    filtered=employees
    if q:
        mask=employees.astype(str).apply(lambda col:col.str.contains(q,case=False,na=False)).any(axis=1)
        filtered=employees[mask]
    st.dataframe(filtered,use_container_width=True,hide_index=True)
    st.subheader("Task instances")
    task_q=st.text_input("Filter tasks by employee ID or task name")
    tf=tasks
    if task_q and not tasks.empty:
        tf=tasks[tasks.astype(str).apply(lambda col:col.str.contains(task_q,case=False,na=False)).any(axis=1)]
    st.dataframe(tf,use_container_width=True,hide_index=True)
with tab4:
    if st.button("Run data validation"):
        result=validate()
        if result["passed"]: st.success("All implemented primary-key and foreign-key checks passed.")
        else: st.error("Validation found issues.")
        st.json(result)
    st.write("Dataset row counts")
    st.dataframe(pd.DataFrame([{"table":p.stem,"rows":len(pd.read_csv(p,keep_default_na=False))} for p in data.glob("*.csv")]),use_container_width=True,hide_index=True)
    st.write("Audit events")
    st.dataframe(audit,use_container_width=True,hide_index=True)
st.caption("All people, emails and serial numbers are synthetic. This demo is not connected to real HR or identity systems.")
