import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';

const output='output/browser-review-tests';await fs.mkdir(output,{recursive:true});
const server=spawn(process.env.PYTHON||'python',['-u','scripts/app_server.py','--port','8876'],{windowsHide:true,stdio:['ignore','pipe','pipe']});
let browser;
try {
  const url=await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(Error('Server did not start')),15000);
    server.once('error',reject);server.once('exit',()=>reject(Error('Server exited')));
    server.stdout.on('data',data=>{const match=String(data).match(/http:\/\/[^\s]+/);if(match){clearTimeout(timer);resolve(match[0]);}});
  });
  browser=await chromium.launch({headless:true,...(process.env.BROWSER_CHANNEL?{channel:process.env.BROWSER_CHANNEL}:{})});
  const fields=JSON.parse(await fs.readFile('examples/pet-bowl-test-fields.json','utf8'));
  const csv=await fs.readFile('examples/pet-bowl-test-observations.csv','utf8');
  const file=(value,name='test.json')=>({name,mimeType:name.endsWith('.csv')?'text/csv':'application/json',buffer:Buffer.from(typeof value==='string'?value:JSON.stringify(value))});
  const reports=[];
  for(const width of [1440,390]){
    const context=await browser.newContext({viewport:{width,height:1000},acceptDownloads:true,reducedMotion:'reduce'});
    const page=await context.newPage();const errors=[];page.on('pageerror',error=>errors.push(error.message));
    let accept=true;page.on('dialog',d=>accept?d.accept():d.dismiss());
    const status=async text=>page.locator('#status').filter({hasText:text}).waitFor();
    const idle=()=>page.waitForFunction(()=>!document.querySelector('#agent-form button[type=submit]').disabled);
    await page.goto(url);await page.getByRole('button',{name:'Load sample',exact:true}).click();await status('Fictional sample loaded');
    await page.getByRole('button',{name:'Analyze observations',exact:true}).click();await status('Review ready');
    await page.getByRole('button',{name:'Tests',exact:true}).click();assert((await page.locator('#report-preview').textContent()).includes('Plan a test'));
    await page.getByRole('button',{name:'Hypotheses',exact:true}).click();await page.getByRole('button',{name:'Try sample hypotheses',exact:true}).click();await status('Citations checked');
    const proposal=page.locator('#hypothesis-P001');await proposal.locator('select').selectOption('test');
    await proposal.locator('textarea').fill('Fictional rehearsal of the paired cleaning task.');await proposal.getByRole('button',{name:'Record choice'}).click();
    const reviewDownload=page.waitForEvent('download');await page.getByRole('button',{name:'Download review',exact:true}).click();
    const review=JSON.parse(await fs.readFile(await(await reviewDownload).path(),'utf8'));await idle();
    await page.getByRole('button',{name:'Define and review a test',exact:true}).click();
    for(const [key,value] of Object.entries(fields)){
      const control=page.locator('#test-'+key);
      if(['proposal_id','direction','data_kind'].includes(key))await control.selectOption(value);else await control.fill(String(value));
    }
    await page.getByRole('button',{name:'Evidence',exact:true}).click();await page.getByRole('button',{name:'Tests',exact:true}).click();
    assert.equal(await page.locator('#test-metric_label').inputValue(),fields.metric_label);
    const axePlan=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();assert.deepEqual(axePlan.violations.map(v=>v.id),[]);
    await page.locator('#report-preview').scrollIntoViewIfNeeded();await page.screenshot({path:`${output}/plan-${width}.png`,fullPage:true});
    await page.getByRole('button',{name:'Record test plan',exact:true}).click();await status('Plan recorded');await idle();
    const planDownload=page.waitForEvent('download');await page.getByRole('button',{name:'Download test plan',exact:true}).click();
    const plan=JSON.parse(await fs.readFile(await(await planDownload).path(),'utf8'));
    assert.deepEqual(plan.fields,fields);
    await page.locator('[data-test-file=observations]').setInputFiles(file(csv,'observations.csv'));await status('Observations checked');await idle();
    assert((await page.locator('#test-result').textContent()).includes('Recorded criteria met'));
    assert((await page.locator('#test-result').textContent()).includes('Fictional exercise'));
    const download=page.waitForEvent('download');await page.getByRole('button',{name:'Download test result',exact:true}).click();
    const result=JSON.parse(await fs.readFile(await(await download).path(),'utf8'));
    assert.equal(result.result.median_improvement,20);assert.equal(result.result.business_effect,'not_established');
    const invalid=csv.replace('100,80','NaN,80');
    await page.locator('[data-test-file=observations]').setInputFiles(file(invalid,'bad.csv'));await status('must be finite');await idle();
    assert((await page.locator('#test-result').textContent()).includes('Recorded criteria met'));
    const changed=structuredClone(plan);changed.fields.min_improvement=1;
    await page.locator('[data-test-file=plan]').setInputFiles(file(changed));await status('Test plan or its evidence changed');await idle();
    assert((await page.locator('#test-result').textContent()).includes('Recorded criteria met'));
    accept=false;await page.getByRole('button',{name:'Start another test',exact:true}).click();
    assert(await page.locator('#test-result').isVisible());accept=true;
    await page.locator('[data-test-file=observations]').setInputFiles(file(csv.replace('100,80,0','100,80,1'),'failure.csv'));await status('Observations checked');await idle();
    assert((await page.locator('#test-result').textContent()).includes('Guardrail exceeded'));
    await page.reload();await page.getByRole('button',{name:'Load sample',exact:true}).click();await status('Fictional sample loaded');
    await page.getByRole('button',{name:'Analyze observations',exact:true}).click();await status('Review ready');
    await page.getByRole('button',{name:'Hypotheses',exact:true}).click();await page.locator('#hypothesis-file').setInputFiles(file(review));await status('Review restored');
    await page.getByRole('button',{name:'Tests',exact:true}).click();
    result.result.median_improvement=99999;result.result.criteria_status='fake';
    await page.locator('[data-test-file=plan]').setInputFiles(file(result));await status('Test restored');await idle();
    assert((await page.locator('#test-result').textContent()).includes('20 seconds'));
    assert((await page.locator('#test-result').textContent()).includes('Recorded criteria met'));
    assert(!(await page.locator('#test-result').textContent()).includes('99999'));
    const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();assert.deepEqual(axe.violations.map(v=>v.id),[]);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    assert.equal((await page.locator('body').textContent()).includes('·'),false);
    await page.locator('#test-result').scrollIntoViewIfNeeded();await page.screenshot({path:`${output}/result-${width}.png`,fullPage:true});
    await page.locator('#brief').fill('Changed study inputs');
    assert(await page.getByRole('button',{name:'Download test result',exact:true}).isDisabled());
    assert(await page.getByRole('button',{name:'Download test plan',exact:true}).isDisabled());
    assert.deepEqual(errors,[]);
    reports.push({width,recorded_plan:true,plan_draft_navigation:true,paired_result:true,guardrail_failure:true,
      invalid_csv_preserves_result:true,changed_plan_rejected:true,cancel_preserves_result:true,reload_and_recompute:true,
      stale_input_disables_export:true,axe_violations:0,overflow:false,page_errors:errors});
    await context.close();
  }
  await fs.writeFile(`${output}/report.json`,JSON.stringify({scope:'Fictional paired tasks, not measured customer outcomes',reports},null,2));console.log(JSON.stringify(reports));
} finally {await browser?.close();if(server.exitCode===null){server.kill();await once(server,'exit');}}
