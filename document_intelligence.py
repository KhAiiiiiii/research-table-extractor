import logging
import pandas as pd
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest

from helper import is_comma_separated_number, strip_comma_thousands, is_percentage_string, convert_percentage_to_decimal

def get_words(page, line):
    result = []
    for word in page.words:
        if _in_span(word, line.spans):
            result.append(word)

    return result

def _in_span(word, spans):
    for span in spans:
        if word.span.offset >= span.offset and (word.span.offset + word.span.length) <= (span.offset + span.length):
            return True
    return False

def process_di(file_bytes, key, endpoint):
    logging.info("Parsing data from file...")

    try:
        client = DocumentIntelligenceClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        poller = client.begin_analyze_document(
            "prebuilt-layout", AnalyzeDocumentRequest(bytes_source=file_bytes
            ))
        result: AnalyzeResult = poller.result()

        return result
    except Exception as e:
        logging.error(f"DI processing failed: {e}")
    
def extract_table_from_result(result: AnalyzeResult, convert_numbers = True, convert_percentages = True):
    if result.tables:
        logging.info(f"Result has tables")
        tables = []

        for table_idx, table in enumerate(result.tables):
            logging.info(f"Processing Table #{table_idx} ({table.row_count},{table.column_count})")
            grid = [["" for _ in range(table.column_count)] for _ in range(table.row_count)]
            dtypes = [ "string" ] * table.column_count

            for cell in table.cells:
                if convert_numbers and is_comma_separated_number(cell.content):
                    dtypes[cell.column_index] = 'number'
                    grid[cell.row_index][cell.column_index] = float(strip_comma_thousands(cell.content))
                    continue

                if convert_percentages and is_percentage_string(cell.content):
                    dtypes[cell.column_index] = 'percentage'
                    grid[cell.row_index][cell.column_index] = float(convert_percentage_to_decimal(cell.content))
                    continue

                grid[cell.row_index][cell.column_index] = cell.content

            df = pd.DataFrame(grid)
            tables.append((df, table_idx, dtypes))
        
        return tables
    else:
        logging.error("DI returned results with no tables")

def save_tables_to_excel(tables: list, filename, convert_numbers = True):
    if len(tables) <= 0:
        return logging.error("Tables cannot be empty")

    logging.info(f"Saving tables to {filename}.xlsx")
    writer = pd.ExcelWriter(f"{filename}.xlsx",
                            engine="xlsxwriter",
                            mode="w",
                            engine_kwargs={"options": {"strings_to_numbers": True if convert_numbers else False}})
    
    for table, table_idx, dtypes in tables:
        ws_name = f"Table {table_idx + 1}"
        table.to_excel(writer,
                        sheet_name=ws_name,
                        header=False,
                        index=False)
        wb = writer.book
        
        # Change column dtypes
        ws = writer.sheets[ws_name]
        for idx, t in enumerate(dtypes):
            match t:
                case "percentage":
                    fmt = wb.add_format({ "num_format": "0.00%" })
                    ws.set_column(idx, idx, None, fmt)
                case "number":
                    fmt = wb.add_format({ "num_format": "#,##0.0;-#,##0.0" })
                    ws.set_column(idx, idx, None, fmt)
        
    writer.close()