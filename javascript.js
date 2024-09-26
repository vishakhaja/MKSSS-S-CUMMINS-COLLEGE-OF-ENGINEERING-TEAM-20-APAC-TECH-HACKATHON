document.addEventListener("DOMContentLoaded", function () {
    const currency1Select = document.getElementById("currency1");
    const currency2Select = document.getElementById("currency2");
    const startDateInput = document.getElementById("start-date");
    const endDateInput = document.getElementById("end-date");
    const fetchButton = document.getElementById("fetch-rates");
    const resultDiv = document.getElementById("result");

    // Function to fetch exchange rates
    async function fetchExchangeRates(currency1, currency2, startDate, endDate) {
        const apiKey = "e9ae395767985c99a6a832eb"; // Replace with your actual API key
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/exchange_rates?currency1=${currency1}&currency2=${currency2}&start_date=${startDate}&end_date=${endDate}&duration=Monthly`, {
                headers: {
                    'Authorization': `Bearer ${apiKey}` // Adjust this based on how your API expects the key
                }
            });
            if (!response.ok) {
                throw new Error(`Error fetching exchange rates: ${response.statusText}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error(error);
            return { error: error.message };
        }
    }
    

    // Function to display results
    function displayResults(data) {
        resultDiv.innerHTML = ""; // Clear previous results
        if (data.error) {
            resultDiv.innerHTML = `<p style="color: red;">${data.error}</p>`;
        } else {
            // Display the fetched exchange rates
            data.forEach(rate => {
                const rateItem = document.createElement("p");
                rateItem.textContent = `Date: ${rate.Date}, Rate: ${rate[currency2Select.value]}`;
                resultDiv.appendChild(rateItem);
            });
        }
    }

    // Event listener for the fetch button
    fetchButton.addEventListener("click", async () => {
        const currency1 = currency1Select.value;
        const currency2 = currency2Select.value;
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;

        const exchangeRates = await fetchExchangeRates(currency1, currency2, startDate, endDate);
        displayResults(exchangeRates);
    });
});
