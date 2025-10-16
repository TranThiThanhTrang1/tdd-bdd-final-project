import logging
from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ID_PREFIX = 'product_'

##################################################################
# Visit Page & Title Checks
##################################################################
@when('I visit the "Home Page"')
def step_impl(context):
    context.driver.get(context.base_url)

@then('I should see "{message}" in the title')
def step_impl(context, message):
    assert message in context.driver.title, f'Expected "{message}" in title but got "{context.driver.title}"'

@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, 'body')
    assert text_string not in element.text, f'Found forbidden text "{text_string}"'

##################################################################
# Field Input & Dropdown
##################################################################
@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)

@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    select = Select(WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.ID, element_id))
    ))
    for option in select.options:
        if option.text.strip().lower() == text.strip().lower():
            option.click()
            return
    raise Exception(f'Cannot find dropdown option: {text}')

@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    select = Select(context.driver.find_element(By.ID, element_id))
    assert select.first_selected_option.text.strip() == text.strip(), \
        f'Expected "{text}" but selected "{select.first_selected_option.text}"'

@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute('value') == '', f'Expected empty field but got "{element.get_attribute("value")}"'

##################################################################
# Copy & Paste Simulation
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    context.last_product_id = element.get_attribute('value')
    logging.info('Saved last_product_id: %s', context.last_product_id)

@when('I paste the saved "Id" field')
def step_impl(context):
    if not hasattr(context, 'last_product_id'):
        raise Exception('No last_product_id found! Did you copy it first?')
    
    element_id = ID_PREFIX + "id"  # giả sử ID field có id="product_id"
    element = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.last_product_id)

@then('the ID should be saved for later use')
def step_impl(context):
    if not hasattr(context, 'last_product_id'):
        raise Exception('No product ID saved in context!')

##################################################################
# Button Clicks
##################################################################
@when('I press the "{button_name}" button')
def step_impl(context, button_name):
    button_id = button_name.lower() + '-btn'
    button = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((By.ID, button_id))
    )
    button.click()

##################################################################
# Flash Message Verification
##################################################################
@then('I should see the message "{message}"')
def step_impl(context, message):
    element = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.ID, 'flash_message'))
    )
    assert message in element.text, f'Expected "{message}" but got "{element.text}"'

##################################################################
# Product List Verification
##################################################################
@then('I should not see "{text}" in the product list')
def step_impl(context, text):
    element = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.ID, 'search_results'))
    )
    assert text not in element.text, f'Found "{text}" in search results'

@then('I should see "{product_name}" in the product list')
def step_impl(context, product_name):
    # đợi dữ liệu trong bảng load xong
    WebDriverWait(context.driver, 20).until(
        lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "#search_results tr")) > 1
    )

    rows = context.driver.find_elements(By.CSS_SELECTOR, "#search_results tr")[1:]  # bỏ header
    found = any(product_name.lower() in row.text.lower() for row in rows)
    assert found, f'Expected "{product_name}" in search results, found "{[row.text for row in rows]}"'

@then('I should see only products with "Category" equal to "{category}"')
def step_impl(context, category):
    element = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.ID, 'search_results'))
    )
    lines = [line for line in element.text.splitlines() if line.strip() and not line.startswith("ID ")]
    for line in lines:
        assert category.upper() in line, f'Line "{line}" không thuộc category "{category}"'

@then('I should see only products with "Available" equal to "{available}"')
def step_impl(context, available):
    element = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.ID, 'search_results'))
    )
    lines = [line for line in element.text.splitlines() if line.strip() and not line.startswith("ID ")]
    for line in lines:
        assert available in line, f'Line "{line}" không đúng Available="{available}"'

##################################################################
# Field Verification & Change
##################################################################
@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    actual = element.get_attribute('value')
    assert actual == text_string, f'Expected "{text_string}" but got "{actual}"'

@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)
