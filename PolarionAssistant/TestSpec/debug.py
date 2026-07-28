import re
description = '''<span style="font-weight: bold;font-size: 10pt;line-height: 1.5;">Check hardware and software requirements</span><br/>
 <br/>
 <span style="font-size: 10pt;line-height: 1.5;">Phase: Installation qualification </span><br/>
 <br/>
 
<table id="polarion_wiki macro name=table" style="width: 712px;margin-left: auto;margin-right: auto;border: 1px solid #CCCCCC;empty-cells: show;border-collapse: collapse;">
  <tbody>
    <tr>
      <th style="font-weight: bold;background-color: #F0F0F0;text-align: left;vertical-align: top;width: 51px;height: 12px;border: 1px solid #CCCCCC;border-top: 1px solid #CCCCCC;border-bottom: 1px solid #CCCCCC;border-right: 1px solid #CCCCCC;border-left: 1px solid #CCCCCC;padding: 5px;">Step</th>
      <th style="font-weight: bold;background-color: #F0F0F0;text-align: left;vertical-align: top;width: 295px;height: 12px;border: 1px solid #CCCCCC;border-top: 1px solid #CCCCCC;border-bottom: 1px solid #CCCCCC;border-right: 1px solid #CCCCCC;border-left: 1px solid #CCCCCC;padding: 5px;">Input / Action</th>
      <th style="font-weight: bold;background-color: #F0F0F0;text-align: left;vertical-align: top;width: 332px;height: 12px;border: 1px solid #CCCCCC;border-top: 1px solid #CCCCCC;border-bottom: 1px solid #CCCCCC;border-right: 1px solid #CCCCCC;border-left: 1px solid #CCCCCC;padding: 5px;">Expected Result</th>
    </tr>
    <tr>
      <td style="text-align: left;vertical-align: top;width: 51px;height: 12px;border: 1px solid #CCCCCC;border-top: 1px solid #CCCCCC;border-bottom: 1px solid #CCCCCC;border-right: 1px solid #CCCCCC;border-left: 1px solid #CCCCCC;padding: 5px;">1</td>
      <td style="text-align: left;vertical-align: top;width: 295px;height: 12px;border: 1px solid #CCCCCC;border-top: 1px solid #CCCCCC;border-bottom: 1px solid #CCCCCC;border-right: 1px solid #CCCCCC;border-left: 1px solid #CCCCCC;padding: 5px;">Check that the hardware and software used meets the minimum requirements of the system as set out in Validation Plan Enterprise Architect v15.0.1514, chapter 6.1</td>
      <td style="text-align: left;vertical-align: top;width: 332px;height: 12px;border: 1px solid #CCCCCC;padding: 5px;">The hardware and software used meets the minimum requirements of the system according to Validation Plan Enterprise Architect v15.0.1514, chapter 6.1.</td>
    </tr>
  </tbody>
</table>'''
test_description = "ASDF"
BEG_STR = f'''<span style="font-weight: bold;font-size: 10pt;line-height: 1.5;">{test_description}</span><br/>
    <br/>
    <span style="font-size: 10pt;line-height: 1.5;">Phase: Installation qualification </span><br/>
    <br/>\n'''
    
if __name__ == "__main__":
    TABLE = "<table"
    pos = description.find(TABLE)
    print (pos)
    SPAN = "</span>"
    
    x = re.search(f">.*{SPAN}", description)
    span_len = len(SPAN)
    modification1 = description[:(x.start()+1)] + "ASDF" + description[(x.end()-len(SPAN)):]
    y = re.search(f"{SPAN}.*{TABLE}", modification1, flags=re.DOTALL)
    #modification2 = modification1[:(y.start()+len(SPAN))] + gg + modification1[(y.end()-len(TABLE)):]
    print(x)
    print(x.start())
    print(x.end())
    print(modification1)
    print("===")
    print(y)
    print(modification2)