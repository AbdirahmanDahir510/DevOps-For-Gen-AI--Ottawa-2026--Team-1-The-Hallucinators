import { useEffect, useState } from "react";
import "./SecurityDashboard.css";

const API_URL = "http://localhost:5000/api/tests";

function SecurityDashboard() {
    const [tests, setTests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // --------------------------------------------------
    // LOAD TEST RESULTS
    // --------------------------------------------------

    const loadTests = async () => {
        setLoading(true);
        setError("");

        try {
            const response = await fetch(API_URL);

            if (!response.ok) {
                throw new Error(
                    `Server returned ${response.status}`
                );
            }

            const data = await response.json();

            setTests(data.tests || []);
        } catch (err) {
            console.error(
                "Failed to load test results:",
                err
            );

            setError(
                "Unable to load security test results."
            );
        } finally {
            setLoading(false);
        }
    };

    // Load results when dashboard opens
    useEffect(() => {
        loadTests();
    }, []);

    // --------------------------------------------------
    // STATISTICS
    // --------------------------------------------------

    const passedTests = tests.filter(
        (test) => test.status === "PASS"
    );

    const failedTests = tests.filter(
        (test) => test.status === "FAIL"
    );

    const reviewTests = tests.filter(
        (test) => test.status === "REVIEW"
    );

    const overallScore =
        tests.length === 0
            ? 0
            : Math.round(
                  (passedTests.length / tests.length) * 100
              );

    // --------------------------------------------------
    // CATEGORY SCORE
    // --------------------------------------------------

    const getCategoryTests = (category) => {
        return tests.filter(
            (test) => test.category === category
        );
    };

    const getCategoryScore = (category) => {
        const categoryTests =
            getCategoryTests(category);

        if (categoryTests.length === 0) {
            return 0;
        }

        const passed = categoryTests.filter(
            (test) => test.status === "PASS"
        ).length;

        return Math.round(
            (passed / categoryTests.length) * 100
        );
    };

    const securityTests =
        getCategoryTests("Security");

    const ragTests =
        getCategoryTests("RAG");

    const chaosTests =
        getCategoryTests("Chaos");

    const securityScore =
        getCategoryScore("Security");

    const ragScore =
        getCategoryScore("RAG");

    const chaosScore =
        getCategoryScore("Chaos");

    // --------------------------------------------------
    // RISK COUNTS
    // --------------------------------------------------

    const highRiskTests = tests.filter(
        (test) =>
            test.severity?.toLowerCase() === "high"
    );

    const mediumRiskTests = tests.filter(
        (test) =>
            test.severity?.toLowerCase() === "medium"
    );

    const lowRiskTests = tests.filter(
        (test) =>
            test.severity?.toLowerCase() === "low"
    );

    // --------------------------------------------------
    // SCORE CLASS
    // --------------------------------------------------

    const getScoreClass = (score) => {
        if (score >= 90) {
            return "score-excellent";
        }

        if (score >= 75) {
            return "score-good";
        }

        if (score >= 50) {
            return "score-warning";
        }

        return "score-danger";
    };

    // --------------------------------------------------
    // LOADING STATE
    // --------------------------------------------------

    if (loading) {
        return (
            <div className="security-dashboard">
                <div className="dashboard-loading">
                    <div className="loading-spinner"></div>

                    <p>
                        Loading security test results...
                    </p>
                </div>
            </div>
        );
    }

    // --------------------------------------------------
    // DASHBOARD
    // --------------------------------------------------

    return (
        <div className="security-dashboard">

            {/* =========================================
                HEADER
            ========================================== */}

            <div className="dashboard-header">

                <div>
                    <p className="dashboard-label">
                        AI ASSURANCE
                    </p>

                    <h1>
                        Security & Resilience Dashboard
                    </h1>

                    <p className="dashboard-description">
                        Monitor prompt-injection,
                        RAG security, and chaos-testing
                        results for the AI chatbot.
                    </p>
                </div>

                <button
                    className="refresh-button"
                    onClick={loadTests}
                >
                    ↻ Refresh Tests
                </button>

            </div>

            {/* =========================================
                ERROR
            ========================================== */}

            {error && (
                <div className="error-banner">
                    <strong>
                        Connection Error
                    </strong>

                    <span>
                        {error}
                    </span>

                    <button
                        onClick={loadTests}
                    >
                        Try Again
                    </button>
                </div>
            )}

            {/* =========================================
                OVERALL SCORE
            ========================================== */}

            <section className="overall-section">

                <div className="overall-card">

                    <div className="overall-score">

                        <div
                            className={`score-circle ${getScoreClass(
                                overallScore
                            )}`}
                        >
                            <span>
                                {overallScore}%
                            </span>
                        </div>

                    </div>

                    <div className="overall-info">

                        <p className="card-label">
                            OVERALL SECURITY SCORE
                        </p>

                        <h2>
                            {overallScore >= 90
                                ? "Excellent"
                                : overallScore >= 75
                                ? "Good"
                                : overallScore >= 50
                                ? "Needs Improvement"
                                : "Critical"}
                        </h2>

                        <p>
                            Based on {tests.length} total
                            security and resilience tests.
                        </p>

                    </div>

                </div>

            </section>

            {/* =========================================
                SUMMARY CARDS
            ========================================== */}

            <section className="summary-grid">

                <SummaryCard
                    title="Tests Run"
                    value={tests.length}
                    icon="🧪"
                />

                <SummaryCard
                    title="Passed"
                    value={passedTests.length}
                    icon="✓"
                    type="success"
                />

                <SummaryCard
                    title="Needs Review"
                    value={reviewTests.length}
                    icon="⚠"
                    type="warning"
                />

                <SummaryCard
                    title="Failed"
                    value={failedTests.length}
                    icon="✕"
                    type="danger"
                />

            </section>

            {/* =========================================
                CATEGORY SCORES
            ========================================== */}

            <section>

                <div className="section-header">

                    <div>
                        <p className="section-label">
                            TEST CATEGORIES
                        </p>

                        <h2>
                            Security Coverage
                        </h2>
                    </div>

                </div>

                <div className="category-grid">

                    <CategoryCard
                        title="Security"
                        description="Prompt injection and security controls"
                        score={securityScore}
                        tests={securityTests.length}
                        icon="🛡️"
                    />

                    <CategoryCard
                        title="RAG Security"
                        description="Document and retrieval attacks"
                        score={ragScore}
                        tests={ragTests.length}
                        icon="📄"
                    />

                    <CategoryCard
                        title="Chaos"
                        description="Failure and resilience testing"
                        score={chaosScore}
                        tests={chaosTests.length}
                        icon="⚡"
                    />

                </div>

            </section>

            {/* =========================================
                RISK OVERVIEW
            ========================================== */}

            <section className="risk-section">

                <div className="section-header">

                    <div>
                        <p className="section-label">
                            RISK ANALYSIS
                        </p>

                        <h2>
                            Risk Overview
                        </h2>
                    </div>

                </div>

                <div className="risk-grid">

                    <RiskCard
                        title="High Risk"
                        count={highRiskTests.length}
                        description="Tests with potentially significant security impact."
                        className="high"
                    />

                    <RiskCard
                        title="Medium Risk"
                        count={mediumRiskTests.length}
                        description="Tests requiring monitoring or additional controls."
                        className="medium"
                    />

                    <RiskCard
                        title="Low Risk"
                        count={lowRiskTests.length}
                        description="Tests with limited potential impact."
                        className="low"
                    />

                </div>

            </section>

            {/* =========================================
                SECURITY TESTS
            ========================================== */}

            <TestSection
                title="Security Tests"
                label="ATTACK TESTING"
                tests={securityTests}
                emptyMessage="No security tests have been recorded."
            />

            {/* =========================================
                RAG TESTS
            ========================================== */}

            <TestSection
                title="RAG Security Tests"
                label="RETRIEVAL TESTING"
                tests={ragTests}
                emptyMessage="No RAG security tests have been recorded."
            />

            {/* =========================================
                CHAOS TESTS
            ========================================== */}

            <TestSection
                title="Chaos Tests"
                label="RESILIENCE TESTING"
                tests={chaosTests}
                emptyMessage="No chaos tests have been recorded."
            />

            {/* =========================================
                FOOTER
            ========================================== */}

            <div className="dashboard-footer">

                <p>
                    AI Security & Resilience Testing
                </p>

                <p>
                    Results are generated from the
                    application's automated test suite.
                </p>

            </div>

        </div>
    );
}


// ======================================================
// SUMMARY CARD
// ======================================================

function SummaryCard({
    title,
    value,
    icon,
    type = ""
}) {
    return (
        <div
            className={`summary-card ${type}`}
        >

            <div className="summary-icon">
                {icon}
            </div>

            <div>

                <p>
                    {title}
                </p>

                <strong>
                    {value}
                </strong>

            </div>

        </div>
    );
}


// ======================================================
// CATEGORY CARD
// ======================================================

function CategoryCard({
    title,
    description,
    score,
    tests,
    icon
}) {
    const getScoreClass = (score) => {

        if (score >= 90) {
            return "score-excellent";
        }

        if (score >= 75) {
            return "score-good";
        }

        if (score >= 50) {
            return "score-warning";
        }

        return "score-danger";
    };

    return (
        <div className="category-card">

            <div className="category-top">

                <div className="category-icon">
                    {icon}
                </div>

                <div>

                    <h3>
                        {title}
                    </h3>

                    <p>
                        {description}
                    </p>

                </div>

            </div>

            <div className="category-score">

                <strong
                    className={getScoreClass(score)}
                >
                    {score}%
                </strong>

                <span>
                    {tests} tests
                </span>

            </div>

            <div className="progress-container">

                <div
                    className={`progress-bar ${getScoreClass(
                        score
                    )}`}
                    style={{
                        width: `${score}%`
                    }}
                ></div>

            </div>

        </div>
    );
}


// ======================================================
// RISK CARD
// ======================================================

function RiskCard({
    title,
    count,
    description,
    className
}) {
    return (
        <div
            className={`risk-card ${className}`}
        >

            <div className="risk-card-top">

                <div className="risk-indicator"></div>

                <h3>
                    {title}
                </h3>

                <strong>
                    {count}
                </strong>

            </div>

            <p>
                {description}
            </p>

        </div>
    );
}


// ======================================================
// TEST SECTION
// ======================================================

function TestSection({
    title,
    label,
    tests,
    emptyMessage
}) {
    return (
        <section className="test-section">

            <div className="section-header">

                <div>

                    <p className="section-label">
                        {label}
                    </p>

                    <h2>
                        {title}
                    </h2>

                </div>

                <span className="test-count">
                    {tests.length} tests
                </span>

            </div>

            {tests.length === 0 ? (

                <div className="empty-state">
                    <p>
                        {emptyMessage}
                    </p>
                </div>

            ) : (

                <div className="test-list">

                    {tests.map(
                        (test, index) => (

                            <TestCard
                                key={`${test.name}-${index}`}
                                test={test}
                            />

                        )
                    )}

                </div>

            )}

        </section>
    );
}


// ======================================================
// TEST CARD
// ======================================================

function TestCard({ test }) {

    const status =
        test.status?.toUpperCase() || "UNKNOWN";

    const severity =
        test.severity?.toLowerCase() || "unknown";

    const getStatusIcon = () => {

        switch (status) {

            case "PASS":
                return "✓";

            case "FAIL":
                return "✕";

            case "REVIEW":
                return "⚠";

            default:
                return "?";
        }
    };

    return (
        <div className="test-card">

            <div className="test-status-icon">

                <span
                    className={`status-icon ${status.toLowerCase()}`}
                >
                    {getStatusIcon()}
                </span>

            </div>

            <div className="test-information">

                <div className="test-title-row">

                    <h3>
                        {test.name}
                    </h3>

                    <span
                        className={`status-badge ${status.toLowerCase()}`}
                    >
                        {status}
                    </span>

                </div>

                <p>
                    {test.description ||
                        "No description available."}
                </p>

            </div>

            <div className="test-severity">

                <span
                    className={`severity-badge ${severity}`}
                >
                    {test.severity || "Unknown"}
                </span>

            </div>

        </div>
    );
}

export default SecurityDashboard;