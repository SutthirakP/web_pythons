document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.getElementById("items-list");
    const totalCountElem = document.getElementById("total-count")

    tableBody.addEventListener("click", async (event) => {
        const delButton = event.target.closest(".js-delete")
        if(!delButton) return;

        const itemId = delButton.dataset.id;
        if(!confirm(`Delete item #${itemId}`)) return;

        try {
            const response = await fetch(`/items/${itemId}`, {method: "DELETE"});
            if (response.ok){
                const targetRow = document.getElementById(`row-${itemId}`);
                targetRow.remove();
                if (totalCountElem) {
                    const currentTotal = parseInt(totalCountElem.textContent,10)
                    totalCountElem.textContent  = Math.max(0, currentTotal-1);
                }
            } else {
                alert("Failed to delete.")
            }
        } catch(error) {
            console.error(error);
        }
    })
})
