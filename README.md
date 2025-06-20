# [LAMBDA](https://www.polyu.edu.hk/ama/cmfai/lambda.html) - Multi-Agent Data Analysis System
<body>
<!-- <img src="https://github.com/user-attachments/assets/df454158-79e4-4da4-ae03-eb687fe02f16" style="width: 80%"> -->
<!-- <p align="center">
  <img src="https://github.com/user-attachments/assets/6f6d49ef-40b7-46f2-88ae-b8f6d9719c3a" style="width: 600px;">
</p> -->

![lambda_mix](https://github.com/user-attachments/assets/db5574aa-9441-4c9d-b44d-3b225d11e0cc)


We introduce **LAMBDA**, a novel open-source, code-free multi-agent data analysis system that harnesses the power of large models. LAMBDA is designed to address data analysis challenges in complex data-driven applications through the use of innovatively designed data agents that operate iteratively and generatively using natural language.

## Key Features

- **Code-Free Data Analysis**: Perform complex data analysis tasks through human language instruction.
- **Multi-Agent System**: Utilizes two key agent roles, the programmer and the inspector, to generate and debug code seamlessly.
- **User Interface**: This includes a robust user interface that allows direct user intervention in the operational loop.
- **Model Integration**: Flexibly integrates external models and algorithms to cater to customized data analysis needs.
- **Automatic Report Generation**: Concentrate on high-value tasks, rather than spending time and resources on report writing and formatting.
- **Jupyter Notebook Exporting**: Export the code and the results to Jupyter Notebook for reproduction and further analysis flexibly.

## Getting Started
### Installation
First, clone the repository.

```bash
git clone https://github.com/AMA-CMFAI/LAMBDA.git
cd LAMBDA
```

Then, we recommend creating a [Conda](https://docs.conda.io/en/latest/) environment for this project and install the dependencies by following commands:
```bash
conda create -n lambda python=3.10
conda activate lambda
```

Then, install the required packages:
```bash
pip install -r requirements.txt
```

Next, you should install the Jupyter kernel to create a local Code Interpreter:
```bash
ipython kernel install --name lambda --user
```

### Configuration to Easy Start
1. To use the Large Language Models, you should have an API key from [OpenAI](https://openai.com/api/pricing/) or other companies. Besides, we support OpenAI-Style interface for your local LLMs once deployed, available frameworks such as [Ollama](https://ollama.com/), [LiteLLM](https://docs.litellm.ai/docs/), [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory).
> Here are some products that offer free APIkeys for your reference: [OpenRouter](https://openrouter.ai/) and [SILICONFLOW](https://siliconflow.cn/)
2. Set your API key, models and working path in the config.yaml:
```bash
#================================================================================================
#                                       Config of the LLMs
#================================================================================================
conv_model : "gpt-4o-mini" # the conversation model
programmer_model : "gpt-4o-mini"
inspector_model : "gpt-4o-mini"
api_key : ""
base_url_conv_model : 'https://api.openai.com/v1'
base_url_programmer : 'https://api.openai.com/v1'
base_url_inspector : 'https://api.openai.com/v1'


#================================================================================================
#                                       Config of the system
#================================================================================================
streaming : True
project_cache_path : "cache/conv_cache/" # local cache path
max_attempts : 5 # The max attempts of self-correcting
max_exe_time: 18000 # max time for the execution

#knowledge integration
retrieval : False # whether to start a knowledge retrieval. If you don't create your knowledge base, you should set it to False
```

Finally, run the following command to start the LAMBDA with GUI:
```bash
python app.py
```


## Demonstration Videos

The performance of LAMBDA in solving data science problems is demonstrated in several case studies, including:
- **[Data Analysis](https://www.polyu.edu.hk/ama/cmfai/files/lambda/lambda.mp4)**
- **[Integrating Human Intelligence](https://www.polyu.edu.hk/ama/cmfai/files/lambda/knw.mp4)**
- **[Education](https://www.polyu.edu.hk/ama/cmfai/files/lambda/LAMBDA_education.mp4)**

## Updating History
- [2025-02-26] Remove the cloud cache module for easier use. Code refactoring.

## Planning works
- [High] Replace Gradio UI with OpenWebUI.
- [High] Refactor the Knowledge Integration and Knowledge base module by ChromaDB.
- [High] Add a Docker image for easier use.
- Documentation writing.



## Related Works
If you are interested in Data Agent, you can take a look at :
- Our survey paper [[A Survey on Large Language Model-based Agents for Statistics and Data Science]](https://www.arxiv.org/pdf/2412.14222)
- and a reading list: [[Paper List of LLM-based Data Science Agents]](https://github.com/Stephen-SMJ/Reading-List-of-Large-Language-Model-Based-Data-Science-Agent)


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



## Acknowledgements

Thank the contributors and the communities for their support and feedback.

---

> If you find our work useful in your research, consider citing our paper by:



```bash
 @article{sun2024lambda,
  title={LAMBDA: A Large Model Based Data Agent},
  author={Sun, Maojun and Han, Ruijian and Jiang, Binyan and Qi, Houduo and Sun, Defeng and Yuan, Yancheng and Huang, Jian},
  journal={arXiv preprint arXiv:2407.17535},
  year={2024}
}

@article{sun2024survey,
  title={A Survey on Large Language Model-based Agents for Statistics and Data Science},
  author={Sun, Maojun and Han, Ruijian and Jiang, Binyan and Qi, Houduo and Sun, Defeng and Yuan, Yancheng and Huang, Jian},
  journal={arXiv preprint arXiv:2412.14222},
  year={2024}
}
```
## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Stephen-SMJ/LAMBDA&type=Timeline)](https://star-history.com/#Stephen-SMJ/LAMBDA&Timeline)
</body>
