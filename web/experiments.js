const make = (tag, text, className) => {
  const node = document.createElement(tag);
  if (text != null) node.textContent = String(text).replaceAll('·', ' ');
  if (className) node.className = className;
  return node;
};
const verdicts = {criteria_met:'Recorded criteria met', need_more_pairs:'Collect more paired observations',
  guardrail_exceeded:'Guardrail exceeded', improvement_below_target:'Improvement below target'};

export class TestWorkbench {
  constructor(options) { Object.assign(this, options); this.clear(); }
  clear() { this.plan=null;this.result=null;this.draft={}; }
  hasWork() { return !!this.plan || Object.keys(this.draft).length>0; }
  async post(url, fields) {
    return this.request(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...this.context(),...fields})});
  }
  button(label, callback) {
    const button=make('button',label,'secondary-button');button.type='button';button.dataset.reviewControl='';
    button.addEventListener('click',callback);return button;
  }
  inputFile(parent, label, accept, action) {
    const input=make('input');input.type='file';input.accept=accept;input.hidden=true;input.dataset.reviewControl='';
    input.dataset.testFile=accept.includes('csv')?'observations':'plan';
    input.addEventListener('change',()=>{
      const file=input.files[0];input.value='';if(!file)return;
      this.run(async()=>{
        if(file.size>2_000_000)throw Error('Keep the imported file under 2 MB. Existing work is unchanged.');
        const text=new TextDecoder('utf-8',{fatal:true}).decode(await file.arrayBuffer());
        return action(text);
      });
    });
    parent.append(this.button(label,()=>input.click()),input);
  }
  render(root) {
    root.append(make('h3','Check a planned test'));
    const ctx=this.context();
    const eligible=ctx?.review?.entries.filter(row=>row.choice==='test')||[];
    if(!eligible.length) {
      root.append(make('p','Choose Plan a test and record your reason in Hypotheses first.'));
      return;
    }
    const actions=make('div',null,'review-actions');
    this.inputFile(actions,'Import test plan or result','.json,application/json',async text=>{
      const data=JSON.parse(text);
      const isResult=data?.kind==='market-test-result';
      if(isResult && data.schema_version!=='1.0')throw Error('Unsupported test result version.');
      const plan=isResult?data.plan:data;
      const checked=await this.post(isResult?'/api/test-result':'/api/test-plan',isResult?
        {plan,observations_csv:data.observations_csv}:{plan});
      return ()=>{
        if(this.hasWork()&&!confirm('Replace the current test? Download it first to keep a copy.'))return;
        this.plan=isResult?checked.package.plan:checked.plan;this.result=isResult?checked:null;this.draft={};
        this.status('Test restored and checked against the current hypothesis.');
      };
    });
    if(this.plan) actions.append(this.button('Start another test',()=>{
      if(confirm('Clear this test from the workspace? Download the plan or result first to keep it.')){
        this.clear();this.renderAll();this.status('Choose the next hypothesis and define its test.');
      }
    }));
    root.append(actions);
    if(!this.plan){this.renderPlan(root,ctx,eligible);return;}
    if(this.plan.analysis_id!==ctx.analysis.analysis_id || this.plan.decisions_id!==ctx.review.decisions_id ||
       !eligible.some(row=>row.proposal_id===this.plan.fields.proposal_id)) {
      root.append(make('p','This plan belongs to different evidence, hypotheses or review choices. Restore the matching review before using its results.','stale-notice'));
      return;
    }
    const f=this.plan.fields;
    root.append(make('h4',f.metric_label));
    const planSection=make(this.result?'details':'section');
    if(this.result)planSection.append(make('summary','Recorded plan and collection method'));
    const summary=make('dl',null,'test-summary');
    for(const [name,value] of [['Hypothesis',f.proposal_id],['Collection',f.collection_method],
      ['Target',`Median paired improvement ≥ ${f.min_improvement} ${f.unit}; ${f.direction} is better`],
      ['Minimum pairs',f.min_pairs],['Guardrail',`${f.guardrail_label}; at most ${f.max_guardrail_rate*100}% of pairs`],
      ['Data',f.data_kind==='synthetic'?'Fictional exercise':'Provided observations, not independently verified']])
      summary.append(make('dt',name),make('dd',value));
    planSection.append(summary);root.append(planSection);
    const tools=make('div',null,'review-actions');
    tools.append(this.button('Download test plan',()=>this.download('market-test-plan.json',JSON.stringify(this.plan,null,2),'application/json')));
    tools.append(this.button('Download observation template',()=>this.download('paired-observations.csv',
      'pair_id,baseline,candidate,guardrail_failed,source_ref\n','text/csv;charset=utf-8')));
    this.inputFile(tools,'Import observations CSV','.csv,text/csv',async text=>{
      const result=await this.post('/api/test-result',{plan:this.plan,observations_csv:text});
      return ()=>{this.result=result;this.status('Observations checked against the recorded criteria.');};
    });
    root.append(tools);
    const help=make('details');help.append(make('summary','How to record paired observations'),
      make('p',`One row per independent pair: baseline and candidate in ${f.unit}, guardrail_failed as 0 or 1, and a source_ref pointing to the observation record. Use anonymous IDs. Missing values are rejected, not converted to zero.`),
      make('p','Use the same task and conditions for each pair. Counterbalance order where appropriate. These descriptive checks do not establish statistical significance or launch readiness.'));
    root.append(help);
    if(!this.result)return;
    const r=this.result.package.result;
    const section=make('section',null,'test-result');section.id='test-result';section.tabIndex=-1;
    section.append(make('h4',verdicts[r.criteria_status]),
      make('p',r.evidence_status==='synthetic_exercise'?'Fictional exercise. No user outcome measured.':'Provided observations. Source authenticity and user outcomes have not been independently verified.','field-help'));
    const results=make('dl',null,'test-summary');
    for(const [name,value] of [['Paired observations',`${r.pair_count} / minimum ${f.min_pairs}`],
      ['Median within-pair improvement',`${r.median_improvement} ${f.unit}`],
      ['Guardrail failures',`${r.guardrail_failures} / ${r.pair_count}`]])results.append(make('dt',name),make('dd',value));
    section.append(results);
    const exports=make('div',null,'review-actions');
    exports.append(this.button('Download test result',()=>this.download('market-test-result.json',JSON.stringify(this.result.package,null,2),'application/json')),
      this.button('Download test notes',()=>this.download('market-test-result.md',this.result.markdown,'text/markdown;charset=utf-8')));
    section.append(exports);root.insertBefore(section,planSection);
  }
  renderPlan(root,ctx,eligible) {
    root.append(make('p','For paired task comparisons, define the measure and thresholds before collecting observations.','field-help'));
    const form=make('form',null,'test-plan-form');
    const config=[['proposal_id','Hypothesis','select',eligible.map(row=>[row.proposal_id,
      `${row.proposal_id}: ${ctx.decisions.proposals[Number(row.proposal_id.slice(1))-1].title}`])],
      ['metric_label','Primary measure','text'],['unit','Unit','text'],
      ['collection_method','Task, conditions and observation source','textarea'],
      ['direction','Better when','select',[['lower','Lower'],['higher','Higher']]],
      ['min_improvement','Minimum useful improvement','number'],['min_pairs','Minimum independent pairs','number'],
      ['guardrail_label','What counts as a guardrail failure?','text'],
      ['max_guardrail_rate','Maximum failure rate (0 to 1)','number'],
      ['data_kind','Data type','select',[['synthetic','Fictional exercise'],['provided','Provided observations']]]];
    const controls={};
    for(const [key,title,type,options] of config){
      const label=make('label',title);label.htmlFor='test-'+key;
      const field=make(type==='select'?'select':type==='textarea'?'textarea':'input');
      field.id='test-'+key;field.name=key;field.required=true;field.dataset.reviewControl='';
      if(type==='select')for(const [value,text] of options){const option=make('option',text);option.value=value;field.append(option);}
      else if(type==='number'){
        field.type='number';field.min=key==='min_pairs'?'2':key==='min_improvement'?'0.000000001':'0';
        field.max=key==='max_guardrail_rate'?'1':key==='min_pairs'?'1000':'1000000000';field.step=key==='min_pairs'?'1':'any';
      }else {if(type==='text')field.type='text';field.maxLength=key==='unit'?60:1000;}
      if(this.draft[key]!==undefined)field.value=this.draft[key];
      field.addEventListener('input',()=>{this.draft[key]=field.value;});
      controls[key]=field;const group=make('div');group.append(label,field);form.append(group);
    }
    const button=this.button('Record test plan',()=>{});button.type='submit';button.className='primary-button';form.append(button);
    form.addEventListener('submit',event=>{
      event.preventDefault();const fields={};
      for(const [key,field] of Object.entries(controls))fields[key]=field.type==='number'?Number(field.value):field.value;
      this.run(async()=>{
        const result=await this.post('/api/test-plan',{fields});
        return ()=>{this.plan=result.plan;this.draft={};this.result=null;this.status('Plan recorded. Download it before collecting observations.');};
      });
    });root.append(form);
  }
}
