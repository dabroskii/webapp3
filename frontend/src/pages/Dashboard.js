import React, { useEffect, useState, useCallback } from "react";
import axiosInstance from "../services/axios";

const Dashboard = ({ loggedInUser, handleLogout }) => {
  const [claims, setClaims] = useState({ pending: [], approved: [], rejected: [] });
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showUpdateForm, setShowUpdateForm] = useState(false);
  const [currentClaimId, setCurrentClaimId] = useState(null);
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    expense_date: "",
    amount: "",
    purpose: "",
    project_id: "",
    currency_id: "",
    charge_to_default_dept: false,
    alternative_dept_code: "",
    follow_up: false,
    previous_claim_id: "",
    invoice: null,
  });

  // Fetch claims
  const fetchClaims = useCallback(async () => {
    try {
      const response = await axiosInstance.get("/claims/dashboard");
      setClaims(response.data);
    } catch (err) {
      console.error("Failed to fetch claims:", err.response?.data || err.message);
      if (err.response?.status === 401) {
        alert("Session expired. Please log in again.");
        handleLogout();
      }
    }
  }, [handleLogout]);

  useEffect(() => {
    fetchClaims();
  }, [fetchClaims]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleFileChange = (e) => {
    setFormData({ ...formData, invoice: e.target.files[0] });
  };

  const handleCreateClaim = async () => {
    try {
      const formDataToSend = new FormData();
      formDataToSend.append("ProjectID", formData.project_id);
      formDataToSend.append("CurrencyID", formData.currency_id);
      formDataToSend.append("ExpenseDate", formData.expense_date);
      formDataToSend.append("Amount", formData.amount);
      formDataToSend.append("Purpose", formData.purpose);
      formDataToSend.append("Status", "Pending");
      formDataToSend.append(
        "ChargeToDefaultDept",
        formData.charge_to_default_dept ? "true" : "false"
      );
      formDataToSend.append("AlternativeDeptCode", formData.alternative_dept_code);

      if (formData.invoice) {
        formDataToSend.append("invoice", formData.invoice);
      }

      if (formData.follow_up) {
        formDataToSend.append("FollowUp", formData.follow_up ? "true" : "false");
        formDataToSend.append("PreviousClaimID", formData.previous_claim_id);
      }

      await axiosInstance.post("/claims", formDataToSend, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      alert("Claim created successfully!");
      fetchClaims();
      setShowCreateForm(false);
    } catch (err) {
      console.error("Failed to create claim:", err.response?.data || err.message);
      alert("Failed to create claim");
    }
  };

  const handleDeleteClaim = async (claimId) => {
    try {
      await axiosInstance.delete(`/claims/${claimId}`);
      alert("Claim deleted successfully!");
      fetchClaims();
    } catch (err) {
      console.error("Failed to delete claim:", err.response?.data || err.message);
      alert("Failed to delete claim");
    }
  };

  const openCreateForm = () => {
    setFormData({
      first_name: "",
      last_name: "",
      expense_date: "",
      amount: "",
      project_id: "",
      currency_id: "",
      purpose: "",
      charge_to_default_dept: true,
      alternative_dept_code: "",
      follow_up: false,
      previous_claim_id: "",
      invoice: null,
    });
    setShowCreateForm(true);
  };

  const openUpdateForm = (claim) => {
    setFormData({
      first_name: "",
      last_name: "",
      expense_date: claim.ExpenseDate ? claim.ExpenseDate.split("T")[0] : "",
      amount: claim.Amount || "",
      purpose: claim.Purpose || "",
      project_id: claim.ProjectID,
      currency_id: claim.Currency,
      charge_to_default_dept: claim.ChargeToDefaultDept || false,
      alternative_dept_code: claim.AlternativeDeptCode || "",
      follow_up: claim.FollowUp || false,
      previous_claim_id: claim.PreviousClaimID || "",
      invoice: null,
    });
    setCurrentClaimId(claim.ClaimID);
    setShowUpdateForm(true);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex justify-center items-center">
      <div className="w-full max-w-6xl bg-white rounded-lg shadow-lg p-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <button
            onClick={openCreateForm}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Create Claim
          </button>
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
          >
            Logout
          </button>
        </div>

        {/* Welcome Message */}
        <h2 className="text-3xl font-bold text-center text-gray-700 mb-8">
          Welcome, {loggedInUser}
        </h2>

        {/* Create Form */}
        {showCreateForm && (
          <div className="border border-gray-300 rounded-lg p-6 mb-6 bg-gray-50">
            <h3 className="text-lg font-bold mb-4">Create New Claim</h3>
            <form className="space-y-4">
              <input
                name="first_name"
                placeholder="First Name"
                value={formData.first_name}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
              />
              <input
                name="last_name"
                placeholder="Last Name"
                value={formData.last_name}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
              />
              <input
                name="expense_date"
                type="date"
                value={formData.expense_date}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
              />
              <input
                name="amount"
                placeholder="Amount"
                value={formData.amount}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
              />
              <input
                name="project_id"
                placeholder="Project ID"
                value={formData.project_id}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
              />
              <input
                name="currency_id"
                placeholder="Currency ID"
                value={formData.currency_id}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
              />
              <label className="block">
                <span className="text-gray-700">Invoice</span>
                <input
                  type="file"
                  name="invoice"
                  onChange={handleFileChange}
                  className="mt-1 block w-full border border-gray-300 rounded"
                />
              </label>
              <label className="block">
                <span className="text-gray-700">Is this a follow-up?</span>
                <input
                  type="checkbox"
                  name="follow_up"
                  checked={formData.follow_up}
                  onChange={(e) =>
                    setFormData({ ...formData, follow_up: e.target.checked })
                  }
                  className="ml-2"
                />
              </label>
              {formData.follow_up && (
                <input
                  name="previous_claim_id"
                  placeholder="Previous Claim ID"
                  value={formData.previous_claim_id}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                />
              )}
              <div className="flex justify-between mt-4">
                <button
                  type="button"
                  onClick={handleCreateClaim}
                  className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                >
                  Submit
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 bg-gray-300 text-black rounded hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {showUpdateForm && (
          <div className="border border-gray-300 rounded p-4 mb-6">
            <h3 className="text-lg font-bold mb-4">Update Claim</h3>
            <form className="space-y-4">
              <input
                name="amount"
                placeholder="Amount"
                value={formData.amount}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded"
              />
              <div className="flex justify-between mt-4">
                <button
                  type="button"
                  onClick={async () => {
                    try {
                      await axiosInstance.put(`/claims/${currentClaimId}`, formData);
                      alert("Claim updated successfully!");
                      fetchClaims();
                      setShowUpdateForm(false);
                    } catch (err) {
                      console.error("Failed to update claim:", err.response?.data || err.message);
                      alert("Failed to update claim");
                    }
                  }}
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  Update
                </button>
                <button
                  type="button"
                  onClick={() => setShowUpdateForm(false)}
                  className="px-4 py-2 bg-gray-300 text-black rounded hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}


        {/* Claims Tables */}
        {["pending", "approved", "rejected"].map((status) => (
          <div key={status} className="border border-gray-300 rounded-lg p-6 mb-6 bg-gray-50">
            <h3 className="text-xl font-bold mb-4 capitalize">{status} Claims</h3>
            {claims[status].length === 0 ? (
              <p className="text-gray-500">No {status} claims available.</p>
            ) : (
              <table className="w-full border-collapse">
                <thead>
                  <tr>
                    <th className="border border-gray-300 px-4 py-2">Claim ID</th>
                    <th className="border border-gray-300 px-4 py-2">Project ID</th>
                    <th className="border border-gray-300 px-4 py-2">Currency</th>
                    <th className="border border-gray-300 px-4 py-2">Amount</th>
                    <th className="border border-gray-300 px-4 py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {claims[status].map((claim) => (
                    <tr key={claim.ClaimID} className="hover:bg-gray-100">
                      <td className="border border-gray-300 px-4 py-2">{claim.ClaimID}</td>
                      <td className="border border-gray-300 px-4 py-2">{claim.ProjectID}</td>
                      <td className="border border-gray-300 px-4 py-2">{claim.Currency}</td>
                      <td className="border border-gray-300 px-4 py-2">${claim.Amount}</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        {status === "approved" ? (
                          <span className="text-gray-500">No Actions Allowed</span>
                        ) : (
                          <>
                            <button
                              onClick={() => openUpdateForm(claim)}
                              className="px-2 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600 mr-2"
                            >
                              Update
                            </button>
                            <button
                              onClick={() => handleDeleteClaim(claim.ClaimID)}
                              className="px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                            >
                              Delete
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;