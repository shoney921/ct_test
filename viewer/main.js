let workbook, worksheet;

document.getElementById("fileInput").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const arrayBuffer = await file.arrayBuffer();
  workbook = new ExcelJS.Workbook();
  await workbook.xlsx.load(arrayBuffer);

  worksheet = workbook.worksheets[0]; // 첫 번째 시트 사용
  renderTable(worksheet);
  document.getElementById("exportBtn").style.display = "inline-block";
});

function renderTable(worksheet) {
  const container = document.getElementById("excelViewer");
  container.innerHTML = "";

  const table = document.createElement("table");
  const maxRow = worksheet.rowCount;

  // 실제 데이터가 있는 열의 최대 개수 계산
  const sheetValues = worksheet.getSheetValues();
  let maxCol = 0;
  for (let r = 1; r < sheetValues.length; r++) {
    if (sheetValues[r] && sheetValues[r].length - 1 > maxCol) {
      maxCol = sheetValues[r].length - 1;
    }
  }

  // 헤더
  const thead = document.createElement("thead");
  const headerRow = document.createElement("tr");
  headerRow.appendChild(document.createElement("th")); // 좌상단 빈칸
  for (let c = 1; c <= maxCol; c++) {
    const th = document.createElement("th");
    th.textContent = String.fromCharCode(64 + c); // A, B, C...
    headerRow.appendChild(th);
  }
  thead.appendChild(headerRow);
  table.appendChild(thead);

  // 바디
  const tbody = document.createElement("tbody");
  for (let r = 1; r <= maxRow; r++) {
    const tr = document.createElement("tr");
    const rowHeader = document.createElement("th");
    rowHeader.textContent = r;
    tr.appendChild(rowHeader);

    for (let c = 1; c <= maxCol; c++) {
      const td = document.createElement("td");
      const cell = worksheet.getCell(r, c);
      const input = document.createElement("input");
      input.type = "text";
      let displayValue = "";
      if (cell.value == null) {
        displayValue = "";
      } else if (typeof cell.value === "object") {
        // 날짜, 수식, 하이퍼링크 등 처리
        if (cell.value.text) {
          displayValue = cell.value.text; // rich text, hyperlink 등
        } else if (cell.value.result) {
          displayValue = cell.value.result; // 수식 결과
        } else if (cell.value.formula) {
          displayValue = cell.value.formula; // 수식 자체
        } else if (cell.value.richText) {
          displayValue = cell.value.richText.map((rt) => rt.text).join("");
        } else if (cell.value instanceof Date) {
          displayValue = cell.value.toLocaleString();
        } else {
          displayValue = JSON.stringify(cell.value); // 기타 객체
        }
      } else {
        displayValue = cell.value;
      }
      input.value = displayValue;
      input.dataset.row = r;
      input.dataset.col = c;
      input.addEventListener("change", (e) => {
        const row = parseInt(e.target.dataset.row);
        const col = parseInt(e.target.dataset.col);
        worksheet.getCell(row, col).value = e.target.value;
      });
      td.appendChild(input);
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);
  container.appendChild(table);
}

document.getElementById("exportBtn").addEventListener("click", async () => {
  if (!workbook) return;
  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "수정된_엑셀.xlsx";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
});
