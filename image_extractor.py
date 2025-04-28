import os
import json
import boto3
import base64
from PIL import Image
from io import BytesIO
import os
from typing import List, Dict, Optional
import csv
import os


model_inference_Id = "XXXXXXXXXXXXX"
region_name = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

# Initialize the Bedrock client
bedrock = boto3.client(
    "bedrock-runtime",
    region_name=region_name,
    aws_access_key_id="XXXXX",
    aws_secret_access_key="XXXX"
)

def encode_image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def get_media_type(ext: str) -> str:
    ext = ext.lower()
    if ext in ("jpg", "jpeg"):
        return "image/jpeg"
    if ext == "png":
        return "image/png"
    if ext == "gif":
        return "image/gif"
    if ext == "webp":
        return "image/webp"
    raise ValueError(f"Unsupported image extension: {ext}")

def get_bedrock_response_with_image(question: str, image_path: str, max_tokens: int = 8000) -> str:
    img_b64 = encode_image_to_base64(image_path)
    ext = image_path.rsplit(".", 1)[-1]
    media_type = get_media_type(ext)

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": img_b64
                        }
                    },
                    {
                        "type": "text",
                        "text": question
                    }
                ]
            }
        ]
    }

    response = bedrock.invoke_model(
        body=json.dumps(body),
        modelId=model_inference_Id,
        accept='application/json',
        contentType='application/json'
    )
    resp = json.loads(response['body'].read())
    return resp['content'][0]['text']


def extract_dict_from_response(response: str) -> Optional[Dict]:
    """
    Safely extracts a dictionary from a string response by finding the first { and last }.
    Returns None if no valid dictionary is found.
    """
    try:
        start = response.find('{')
        end = response.rfind('}')
        
        if start == -1 or end == -1:
            return None
            
        json_str = response[start:end+1]
        return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError):
        return None

def process_images_in_folder(folder_path: str) -> List[Dict[str, str]]:
    """
    Process all images in a specified folder, extracting text explanations from each image.
    Returns a list of dictionaries containing the question-answer pairs for each image.
    """
    domains =  """
            Domain 1: SDLC Automation
        CI/CD Pipelines: Set up build, test, and deployment automation (CodeBuild, CodeDeploy, Secrets Manager).

        Automated Testing: Integrate unit, integration, and security tests in pipelines.

        Artifact Management: Securely store and manage build artifacts (S3, ECR, CodeArtifact).

        Deployment Strategies: Implement blue/green, canary, and immutable deployments for EC2, containers, and serverless.

        Domain 2: Configuration Management & IaC
        IaC: Use CloudFormation, CDK, or SAM to automate infrastructure.

        Multi-Account Automation: Manage accounts with AWS Organizations, Control Tower, and IAM policies.

        Large-Scale Automation: Automate patching, compliance, and workflows using Systems Manager & Lambda.

        Domain 3: Resilient Cloud Solutions
        High Availability: Multi-AZ/multi-Region setups, failover, and load balancing.

        Scalability: Auto Scaling, serverless, and containerized workloads (ECS, EKS).

        Disaster Recovery: Backup strategies, RTO/RPO compliance, and automated recovery.

        Domain 4: Monitoring & Logging
        Log & Metric Collection: Use CloudWatch, Kinesis, and X-Ray for monitoring.

        Analysis & Alerts: Create dashboards, detect anomalies, and set up alarms.

        Automation: Trigger actions via EventBridge, SNS, and Lambda for event-driven responses.

        Domain 5: Incident & Event Response
        Event Processing: Use EventBridge, SQS, and Step Functions for workflows.

        Automated Remediation: Fix issues with Systems Manager and AWS Config.

        Troubleshooting: Analyze failures using CloudWatch, X-Ray, and deployment logs.

        Domain 6: Security & Compliance
        IAM at Scale: Least privilege, role-based access, and automated credential rotation.

        Security Automation: Enforce controls via Security Hub, WAF, KMS, and Macie.

        Auditing & Monitoring: Track threats with GuardDuty, Inspector, and CloudTrail.
    """

    prompt = (
        "the image comprieses of a question, along with multiple choice questiong and a correct answer, extract the question, multiple choice options and correct answer ",
        "classify the question along with its multiple choice options, and match it to the closest domain from the 6 domains",
        "Your response must be a valid JSON object with a question along with its multiple cloices, the answer and the domain class",
        "the structure {'question_and_options': '...', 'answer': '...','domain_class':'..'}",
        rf"domains = --start domains--{domains} --end domains--"
    )
    
    responses = []
    supported_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    
    if not os.path.isdir(folder_path):
        print(f"[ERROR] Invalid folder path: {folder_path}")
        return responses
    
    print(f"\nProcessing images in: {folder_path}")
    
    for filename in sorted(os.listdir(folder_path)):
        if not filename.lower().endswith(supported_extensions):
            continue
            
        image_path = os.path.join(folder_path, filename)
        print(f"\n* Processing: {filename}")
        
        try:
            raw_response = get_bedrock_response_with_image(str(prompt), image_path)
            
            # Extract the dictionary from the response
            response_dict = extract_dict_from_response(str(raw_response))
            
            if not response_dict:
                print(f"[WARNING] No valid JSON found in response for {filename}")
                responses.append({
                    'image': filename,
                    'image_path': image_path,
                    'error': 'Invalid response format - no JSON found'
                })
                continue
                
            # Validate we got the expected structure
            if not all(key in response_dict for key in ['question_and_options', 'answer','domain_class']):
                print(f"[WARNING] Missing required keys in response for {filename}")
                responses.append({
                    'image': filename,
                    'image_path': image_path,
                    'error': 'Invalid response format - missing keys',
                    'raw_response': str(raw_response)[:200] + '...'  # Store truncated raw response
                })
                continue
                
            # Successful processing
            result = {
                'question_and_options': response_dict['question_and_options'],
                'answer': response_dict['answer'],
                'domain_class':response_dict['domain_class']
            }
            responses.append(result)
            print(f"[SUCCESS] Processed {filename}")
            
        except Exception as e:
            print(f"[ERROR] Processing {filename}: {str(e)}")
            responses.append({
                'image': filename,
                'image_path': image_path,
                'error': str(e)
            })
    
    print(f"\nCompleted. Processed {len(responses)} images.")
    print(responses)
    return responses

def save_results_to_csv(results, csv_file_path):
    # Filter out items with an 'error' key
    valid_results = [item for item in results if 'error' not in item]

    # If there are no valid results, do nothing
    if not valid_results:
        print("No valid results to save.")
        return

    # Write valid results to CSV
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['question_and_options', 'answer', 'domain_class'])
        writer.writeheader()
        for item in valid_results:
            writer.writerow(item)
    
    print(f"Saved {len(valid_results)} results to {csv_file_path}")

# Example usage
if __name__ == "__main__":
    
    # path to images
    base = os.getcwd()
    results = process_images_in_folder("folderpath")
    save_results_to_csv(results,"folderpath"+rf"\csv.csv")


